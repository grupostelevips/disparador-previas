import os
import json
import time
import threading
import requests
from flask import Flask
from datetime import datetime, timedelta

app = Flask(__name__)

# =====================================================================
# CREDENCIAIS E CONFIGURAÇÕES
# =====================================================================
TOKEN = "9217225194:AAFAs31k38pRQDe7EzXEVISAuc2QQmk2quo"
CHAT_ID = "-1001921257744"  # Grupo de Prévias

# Cole aqui o mesmo LINK_BOT_VENDAS que você já colocou no agendar_geral.py
LINK_BOT_VENDAS = "https://t.me/SEU_BOT_VENDAS_AQUI"

# 17 segundos = ~3,5 vídeos por minuto (mude para 15 para 4/min ou 20 para 3/min)
INTERVALO_SEGUNDOS = 17

# =====================================================================
# COLE AQUI OS 9 FILE_IDs QUE VOCÊ JÁ PREENCHEU NO SEU PC
# =====================================================================
VIDEOS_PREVIAS = [
    "BAACAgEAAxkBAAMLavhS3g6KN1OOceG15XY6BZVGQqkAAiMIAAJe8sBH5GV2TswlYRM9BA",
    "BAACAgEAAxkBAAMDavhS3iaPn30C6-aC1z_6ZENMN5kAAgsIAAJe8sBHnW0mO3Kr1CI9BA",
    "BAACAgEAAxkBAAMEavhS3gx-f6PxBTWTim3Nie0JzOEAAgwIAAJe8sBHe6Egp_NtSrs9BA",
    "BAACAgEAAxkBAAMFavhS3lh8zd81OxlLqMfho0l0jg4AAg0IAAJe8sBHmmhXO6T07es9BA",
    "BAACAgEAAxkBAAMGavhS3s5x276fj9bTxFeXm0jN-ywAAg4IAAJe8sBHGeuRF_3u8M09BA",
    "BAACAgEAAxkBAAMHavhS3rYS9VHI_WVrjSyBm2j67s0AAh4IAAJe8sBHM45KE75-yuk9BA",
    "BAACAgEAAxkBAAMIavhS3iaQq9GMgq038Ul68518MK8AAh8IAAJe8sBHWBZs_mbK-y49BA",
    "BAACAgEAAxkBAAMJavhS3vptWXzNz3JAeN_q1qd4m38AAiEIAAJe8sBHqw6m3TZNdzI9BA",
    "BAACAgEAAxkBAAMKavhS3tF5dQMly-ENBuXCyR3HSw0AAiIIAAJe8sBHS6kBzhyOdp49BA",
]

# COLE AQUI O FILE_ID DO VÍDEO DE REMARKETING PESADO (Enviado a cada 9 prévias)
VIDEO_REMARKETING_PESADO = "BAACAgEAAxkBAAMCavhQUhDE1L6PhoZarFJe5gTEvNYAAgoIAAJe8sBHOUMdPHEeBww9BA"
# =====================================================================
# 4 VARIAÇÕES DE COPY PARA AS PRÉVIAS (Alinhadas com o Funil VIP)
# =====================================================================

COPY_1 = (
    "🔥 <b>ISSO É APENAS 1% DO QUE ROLA NO VIP OFICIAL...</b>\n\n"
    "Aqui no grupo aberto você só vê o corte. Lá dentro o sistema é sem censura e atualizado todos os dias:\n\n"
    "🔞 <b>Casadas no sigilo absoluto</b>\n"
    "📸 <b>Flagras reais e câmeras escondidas</b>\n"
    "📂 <b>Vazados deletados da internet em minutos</b>\n\n"
    "👇 <b>TOQUE ABAIXO PARA LIBERAR SEU ACESSO VITALÍCIO:</b>\n"
    f"👉 {LINK_BOT_VENDAS}"
)

COPY_2 = (
    "👑 <b>CASADAS NO SIGILO E VÍDEOS PROIBIDOS</b> 👑\n\n"
    "O puro suco da traição real! Vídeos gravados escondido que jamais poderiam vazar na internet:\n\n"
    "• Gravando na cama enquanto o marido trabalha\n"
    "• Flagras amadores sem cortes e sem tarjas\n"
    "• Acervo completo liberado na hora via PIX\n\n"
    "⚠️ <i>Sem mensalidade — pagou uma vez, entrou pra sempre.</i>\n\n"
    "👇 <b>GARANTA SUA VAGA NO VIP AGORA:</b>\n"
    f"👉 {LINK_BOT_VENDAS}"
)

COPY_3 = (
    "🔞 <b>O VERDADEIRO SUBMUNDO DOS VAZADOS REAIS</b> 🔞\n\n"
    "Cansado de grupo fake que só enrola? No nosso <b>VIP Oficial</b> você entra na hora e já tem acesso imediato a milhares de vídeos exclusivos:\n\n"
    "✅ Câmeras escondidas e flagras reais\n"
    "✅ Amadoras e vazados inéditos todos os dias\n"
    "✅ Bônus secreto liberado dentro do bot\n\n"
    "👇 <b>CLIQUE E ENTRE ANTES QUE AS VAGAS FECHEM:</b>\n"
    f"👉 {LINK_BOT_VENDAS}"
)

COPY_4 = (
    "💣 <b>TEM UM BÔNUS SECRETO LIBERADO HOJE NO BOT...</b>\n\n"
    "Além de todo o acervo principal com casadas, flagras e câmeras escondidas, quem entrar hoje pelo bot ainda pode desbloquear o <b>Drive Secreto com +400 vídeos amadores</b> sem censura.\n\n"
    "🚨 <i>Oferta válida apenas enquanto o link estiver ativo!</i>\n\n"
    "👇 <b>TOQUE NO BOTÃO E DESBLOQUEIE AGORA:</b>\n"
    f"👉 {LINK_BOT_VENDAS}"
)

LEGENDAS_PREVIAS = [COPY_1, COPY_2, COPY_3, COPY_4]

# =====================================================================
# COPY DO REMARKETING PESADO (Disparado após cada sequência de 9 vídeos)
# =====================================================================
COPY_REMARKETING_PESADO = (
    "🚨 <b>PARE TUDO E LEIA ISSO ANTES QUE ESSE POST SAIA DO AR!</b> 🚨\n\n"
    "Você acabou de ver uma sequência de amostras aqui fora, mas a verdade é uma só: <b>o melhor conteúdo nunca é postado no grupo grátis</b> porque o Telegram derruba.\n\n"
    "🔥 <b>O QUE TE ESPERA AGORA NO VIP OFICIAL:</b>\n"
    "🔞 <b>Casadas no sigilo</b> gravando tudo sem medo\n"
    "📸 <b>Câmeras escondidas</b> e flagras proibidos\n"
    "📂 <b>Vazados raros</b> que somem da internet em 5 minutos\n"
    "💣 <b>Acesso ao Drive Secreto da Novinha de 19 anos</b> (+400 vídeos amadores sem cortes, chorando e implorando)\n\n"
    "✅ <b>ACESSO VITALÍCIO — SEM MENSALIDADE!</b>\n"
    "⚡ <b>Liberação automática e imediata após o PIX.</b>\n\n"
    "⚠️ <i>As vagas promocionais de hoje estão encerrando. Não fique de fora assistindo só migalhas!</i>\n\n"
    "👇 <b>TOQUE NO BOTÃO ABAIXO E GARANTA SEU ACESSO AGORA:</b>\n"
    f"👉 {LINK_BOT_VENDAS}"
)

# Controle de status e trava para não duplicar disparos
status_robo = {
    "ciclo": 0,
    "ultimo_envio": "Iniciando...",
    "total_enviados": 0
}
_lock_inicio = threading.Lock()
_thread_iniciada = False


def enviar_video_id(file_id, legenda, texto_botao):
    """Envia vídeo pelo file_id com legenda HTML e botão inline."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    markup = json.dumps({
        "inline_keyboard": [
            [{"text": texto_botao, "url": LINK_BOT_VENDAS}]
        ]
    })

    payload = {
        "chat_id": CHAT_ID,
        "video": file_id,
        "caption": legenda,
        "parse_mode": "HTML",
        "disable_notification": False,
        "reply_markup": markup,
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
            enviar_video_id(file_id_previa, legenda_atual, "🔥 ENTRAR NO VIP OFICIAL AGORA")
            time.sleep(INTERVALO_SEGUNDOS)

        # 2. Após os 9 vídeos, dispara o vídeo de Remarketing Pesado
        if VIDEO_REMARKETING_PESADO and not VIDEO_REMARKETING_PESADO.startswith("COLE_AQUI"):
            print("🚨 Enviando VÍDEO DE REMARKETING PESADO...")
            enviar_video_id(
                VIDEO_REMARKETING_PESADO,
                COPY_REMARKETING_PESADO,
                "🚨 LIBERAR VIP + DRIVE SECRETO AGORA"
            )
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
