import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# =====================================================================
# CREDENCIAIS E CONFIGURAÇÕES
# =====================================================================
TOKEN = "9217225194:AAFAs31k38pRQDe7EzXEVISAuc2QQmk2quo"
CHAT_ID = "-1001921257744"  # Grupo de Prévias

# Coloque aqui o @ do seu Bot de Vendas VIP (Ex: "@PlayBoxADMVIP_bot")
ARROBA_BOT_VENDAS = "@ADM_TudaoVIP_bot"

# 17 segundos = ~3,5 vídeos por minuto (mude para 15 para 4/min ou 20 para 3/min)
INTERVALO_SEGUNDOS = 17

# Normaliza o @ automaticamente para nunca quebrar o link clicável no Telegram
_bot_limpo = ARROBA_BOT_VENDAS.replace("https://t.me/", "").replace("http://t.me/", "").replace("@", "").strip()
BOT_MENTION = f"@{_bot_limpo}"

# =====================================================================
# MANTENHA AQUI OS SEUS 9 FILE_IDs DOS VÍDEOS DE PRÉVIA
# =====================================================================
VIDEOS_PREVIAS = [
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_1",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_2",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_3",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_4",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_5",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_6",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_7",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_8",
    "COLE_AQUI_O_FILE_ID_DO_VIDEO_9",
]

# MANTENHA AQUI O FILE_ID DO VÍDEO DE REMARKETING PESADO (Enviado a cada 9 prévias)
VIDEO_REMARKETING_PESADO = "COLE_AQUI_O_FILE_ID_DO_VIDEO_REMARKETING_PESADO"

# =====================================================================
# 4 VARIAÇÕES DE COPY PARA AS PRÉVIAS (Sem botão + Fechamento com @)
# =====================================================================

COPY_1 = (
    "🔥 <b>ISSO É APENAS 1% DO QUE ROLA NO VIP OFICIAL</b> ✅\n\n"
    "Aqui no grupo aberto você só vê o corte. Lá dentro o sistema é sem censura e atualizado todos os dias:\n\n"
    "✔️ <b>Casadas no sigilo absoluto</b>\n"
    "✔️ <b>Flagras reais e câmeras escondidas</b>\n"
    "✔️ <b>Vazados deletados da internet em minutos</b>\n"
    "✔️ <b>Acesso vitalício sem mensalidade</b>\n\n"
    "🔒 Acesso imediato após a compra! 👑\n\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !"
)

COPY_2 = (
    "👑 <b>CASADAS NO SIGILO E VÍDEOS PROIBIDOS</b> 👑\n\n"
    "O puro suco da traição real! Vídeos gravados escondido que jamais poderiam vazar na internet:\n\n"
    "✔️ <b>Gravando na cama enquanto o marido trabalha</b>\n"
    "✔️ <b>Flagras amadores sem cortes e sem tarjas</b>\n"
    "✔️ <b>Pagou uma vez, entrou pra sempre</b>\n\n"
    "🔒 Acesso imediato após a compra! 👑\n\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !"
)

COPY_3 = (
    "🔞 <b>O VERDADEIRO SUBMUNDO DOS VAZADOS REAIS</b> 🔞\n\n"
    "Cansado de grupo fake que só enrola? No nosso <b>VIP Oficial</b> você entra na hora com liberação automática via PIX:\n\n"
    "✔️ <b>Câmeras escondidas e flagras reais</b>\n"
    "✔️ <b>Amadoras e vazados inéditos todos os dias</b>\n"
    "✔️ <b>Bônus secreto liberado dentro do bot</b>\n\n"
    "🔒 Acesso imediato após a compra! 👑\n\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !"
)

COPY_4 = (
    "💣 <b>TEM UM BÔNUS SECRETO LIBERADO HOJE NO BOT</b> 💣\n\n"
    "Além de todo o acervo principal com casadas, flagras e câmeras escondidas, quem entrar hoje pelo bot ainda pode desbloquear o <b>Drive Secreto com +400 vídeos amadores</b> sem censura.\n\n"
    "✔️ <b>Sem cortes, sem censura e sem mensalidade</b>\n"
    "✔️ <b>Vagas promocionais encerrando hoje</b>\n\n"
    "🔒 Acesso imediato após a compra! 👑\n\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !"
)

LEGENDAS_PREVIAS = [COPY_1, COPY_2, COPY_3, COPY_4]

# =====================================================================
# COPY DO REMARKETING PESADO (Disparado após cada sequência de 9 vídeos)
# =====================================================================
COPY_REMARKETING_PESADO = (
    "🚨 <b>PARE TUDO E LEIA ISSO ANTES QUE ESSE POST SAIA DO AR!</b> 🚨\n\n"
    "Você acabou de ver uma sequência de amostras aqui fora, mas a verdade é uma só: <b>o melhor conteúdo nunca é postado no grupo grátis</b> porque o Telegram derruba.\n\n"
    "🔥 <b>BENEFÍCIOS EXCLUSIVOS NO VIP OFICIAL:</b> ⤵️\n"
    "✔️ <b>Casadas no sigilo</b> gravando tudo sem medo\n"
    "✔️ <b>Câmeras escondidas</b> e flagras proibidos\n"
    "✔️ <b>Vazados raros</b> que somem da internet em 5 minutos\n"
    "✔️ <b>Drive Secreto da Novinha de 19 anos</b> (+400 vídeos amadores sem cortes)\n"
    "✔️ <b>Acesso vitalício</b> — sem mensalidade\n\n"
    "🔒 Acesso imediato após a compra! 👑\n\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !\n"
    f"📍 Adquira o VIP já: {BOT_MENTION} !"
)

# Controle de status e trava para não duplicar disparos
status_robo = {
    "ciclo": 0,
    "ultimo_envio": "Iniciando...",
    "total_enviados": 0
}
_lock_inicio = threading.Lock()
_thread_iniciada = False


def enviar_video_id(file_id, legenda):
    """Envia vídeo pelo file_id com legenda HTML limpa e sem botão."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"

    payload = {
        "chat_id": CHAT_ID,
        "video": file_id,
        "caption": legenda,
        "parse_mode": "HTML",
        "disable_notification": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        agora = datetime.now().strftime("%d/%m %H:%M:%S")

        if resp.status_code == 200:
            status_robo["ultimo_envio"] = agora
            status_robo["total_enviados"] += 1
            print(f"✅ [{agora}] Vídeo enviado com sucesso! (Total: {status_robo['total_enviados']})")
            return True

        elif resp.status_code == 429:
            dados_erro = resp.json()
            espera = dados_erro.get("parameters", {}).get("retry_after", 30)
            print(f"⏳ [{agora}] Limite de velocidade do Telegram. Pausando {espera}s...")
            time.sleep(espera + 1)
            return False

        else:
            print(f"⚠️ [{agora}] Erro Telegram ({resp.status_code}): {resp.text}")
            return False

    except Exception as e:
        print(f"❌ Erro de conexão ao enviar vídeo: {e}")
        return False


def iniciar_disparos_continuos():
    ids_validos = [vid for vid in VIDEOS_PREVIAS if vid and not vid.startswith("COLE_AQUI")]
    if not ids_validos:
        print("❌ ERRO: Preencha os file_ids na lista VIDEOS_PREVIAS!")
        return

    print("🚀 Disparador de Prévias em Nuvem iniciado!")
    indice_copy = 0
    ciclo_numero = 1

    while True:
        status_robo["ciclo"] = ciclo_numero
        print(f"=== INICIANDO CICLO #{ciclo_numero} ===")

        # 1. Dispara a sequência dos 9 vídeos de prévia
        for num_video, file_id_previa in enumerate(ids_validos, start=1):
            legenda_atual = LEGENDAS_PREVIAS[indice_copy % len(LEGENDAS_PREVIAS)]
            indice_copy += 1

            print(f"🔥 Enviando Prévia {num_video}/{len(ids_validos)}...")
            enviar_video_id(file_id_previa, legenda_atual)
            time.sleep(INTERVALO_SEGUNDOS)

        # 2. Após os 9 vídeos, dispara o vídeo de Remarketing Pesado
        if VIDEO_REMARKETING_PESADO and not VIDEO_REMARKETING_PESADO.startswith("COLE_AQUI"):
            print("🚨 Enviando VÍDEO DE REMARKETING PESADO...")
            enviar_video_id(VIDEO_REMARKETING_PESADO, COPY_REMARKETING_PESADO)
            time.sleep(INTERVALO_SEGUNDOS)

        ciclo_numero += 1


def garantir_thread_ativa():
    global _thread_iniciada
    with _lock_inicio:
        if not _thread_iniciada:
            _thread_iniciada = True
            t = threading.Thread(target=iniciar_disparos_continuos, daemon=True)
            t.start()


# Rota web para o Render manter o serviço ativo e o UptimeRobot pingar
@app.route("/", methods=["GET"])
def home():
    garantir_thread_ativa()
    return (
        f"Disparador de Prévias Ativo! | Ciclo: {status_robo['ciclo']} | "
        f"Vídeos enviados: {status_robo['total_enviados']} | Último envio: {status_robo['ultimo_envio']}",
        200
    )


# Inicia o loop automaticamente assim que o servidor sobe
garantir_thread_ativa()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
