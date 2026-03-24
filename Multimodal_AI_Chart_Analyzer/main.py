import os
import io
import time
import asyncio
import logging
from typing import Dict
from dotenv import load_dotenv

import requests
import google.generativeai as genai
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from PIL import Image

# ==========================================
# Configurações Iniciais e Variáveis
# ==========================================

# Configuração de Logs para depuração limpa
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis do arquivo .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("⚠️ ERRO: TELEGRAM_TOKEN e GEMINI_API_KEY devem estar obrigatóriamente no seu arquivo .env")

# Configurar SDK oficial do Google Gemini
genai.configure(api_key=GEMINI_API_KEY)
safetys = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

# Deixando o motor livre de configurações restritivas de tokens para evitar corte no servidor
model = genai.GenerativeModel('gemini-2.5-flash', safety_settings=safetys)

# Inicializar Bot e Dispatcher do aiogram 3.x (Assíncrono)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Dicionário de cache local leve para controle de rate limit
user_last_request: Dict[int, float] = {}
RATE_LIMIT_SECONDS = 60


# ==========================================
# Funções de IA e Apis Paralelas
# ==========================================

def buscar_noticias(termo_busca: str) -> str:
    """Consome a SerpAPI (Google News) para capturar as manchetes. Retorna string vazia se não houver chave."""
    if not SERPAPI_KEY:
        return "" # Ocultar completamente se a API Key estiver vazia
    
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_news",
        "q": f"{termo_busca} criptomoedas mercado",
        "gl": "br",   
        "hl": "pt",   
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        noticias_str = ""
        news_results = data.get("news_results", [])[:3]
        
        if not news_results:
            return ""
            
        for noticia in news_results:
            titulo = noticia.get("title", "Notícia s/ título")
            link = noticia.get("link", "https://google.com/news")
            fonte = noticia.get("source", {}).get("name", "Mídia")
            noticias_str += f"🔸 {titulo} - {fonte}\n{link}\n\n"
            
        return noticias_str
    except Exception as e:
        logging.error(f"Erro ao requerer do SerpAPI: {e}")
        return ""

async def analisar_imagem_com_gemini(image: Image.Image) -> str:
    """Conecta c/ os sensores do Gemini e realiza leitura complexa técnica de mercado."""
    prompt = """
    ATENÇÃO: IGNORAR QUALQUER TEXTO OU CABEÇALHO NA IMAGEM. NÃO TRANSCREVA AS MENSAGENS. Leia apenas os candles!
    Escreva a análise até o FIM e entregue OBRIGATORIAMENTE a seguinte estrutura completa:
    
    - Resumo Técnico
    - Suportes/Resistências
    - Zonas de Compra
    - Recomendação Final
    """
    
    response = await asyncio.to_thread(
        model.generate_content,
        [prompt, image]
    )
    return response.text.strip()


async def enviar_resposta_longa(message: types.Message, texto_completo: str):
    """Encapsula o envio chunked formatado, fisicamente limitado em no máximo 2 chunks curtos."""
    MAX_LEN = 3500
    
    # Corte drástico: Se por algum milagre o texto passar de 2 pedaços lógicos (7000 chars), a faca decepa ele no seco.
    if len(texto_completo) > (MAX_LEN * 2):
        texto_completo = texto_completo[:(MAX_LEN * 2)]
        
    if len(texto_completo) <= MAX_LEN:
        await message.reply(texto_completo)
        return

    # Divisor preciso para o array de envios
    chunks = [texto_completo[i:i + MAX_LEN] for i in range(0, len(texto_completo), MAX_LEN)]
    
    # Trava absoluta: no máximo 2 partes enviadas! (Parte 1/2 e Parte 2/2)
    chunks = chunks[:2]
    total_parts = len(chunks)
    
    for i, chunk in enumerate(chunks):
        is_last_chunk = (i == total_parts - 1)
        texto_envio = chunk
        
        if not is_last_chunk:
            texto_envio += f"\n\n⬇️ Parte {i+1}/{total_parts} - Continuando..."
        
        try:
            await message.reply(texto_envio)
            if not is_last_chunk:
                # 3.0s de mega-respiro pedido!
                await asyncio.sleep(3.0)
        except TelegramBadRequest as tbo:
            logging.error(f"Erro bad request no chunk {i}: {repr(tbo)}")
        except Exception as ex:
            logging.error(f"Erro ao enviar chunk {i}: {repr(ex)}")


# ==========================================
# Handlers do Aiogram (Recebimento de Chats)
# ==========================================

@dp.message(Command(commands=["start", "help"]))
async def cmd_help(message: types.Message):
    """Callback para a iniciação de diálogo ("/start" "/help")."""
    texto_ajuda = (
        "📊 Bem-vindo(a) ao Chart Analyzer AI Bot! 🤖\n\n"
        "Fui construído para escanear complexidades de gráficos do mercado e dar os resumos e Calls ideais para sua estratégia.\n\n"
        "📌 INSTRUÇÕES PARA UTILIZAÇÃO:\n"
        "1️⃣ Entre na sua corretora favorita / TradingView, ajuste o gráfico à vontade.\n"
        "2️⃣ Extraia um print/ScreenShot.\n"
        "3️⃣ Envie me esta imagem/foto aqui na conversa.\n"
        "4️⃣ Acelerador: Escreva na LEGENDA DA FOTO qual é o ativo (ex: BTC) pra eu rastrear as notícias do dia pra você!\n\n"
        "⏱️ LIMITE ANTISPAM: Uma análise nova a cada 1 minuto (60s)."
    )
    await message.reply(texto_ajuda)

@dp.message(F.photo)
async def processar_grafico(message: types.Message, bot: Bot):
    """Atuação master: captura a foto, extrai dados e lida com alucinações (Spam de OCR)."""
    user_id = message.from_user.id
    agora = time.time()
    
    if user_id in user_last_request:
        tempo_passado = agora - user_last_request[user_id]
        if tempo_passado < RATE_LIMIT_SECONDS:
            espera = int(RATE_LIMIT_SECONDS - tempo_passado)
            await message.reply(f"🚫 Acesso Rápido Demais!\nEspere bater {espera} segundos antes de mandar o próximo gráfico.")
            return

    user_last_request[user_id] = agora
    msg_status = await message.reply("👀 Lendo velas, médias móveis e consultando a web... Segure aí ⏳")
    
    try:
        photo = message.photo[-1]
        
        image_data = io.BytesIO()
        await bot.download(photo, destination=image_data)
        
        try:
            image_data.seek(0)
            image = Image.open(image_data)
        except Exception:
            await msg_status.delete()
            await message.reply("❌ Análise incompleta (resposta longa ou imagem ruim). Envie print maximizado/nítido.")
            return
            
        if image.width < 800 and image.height < 800:
            await msg_status.delete()
            await message.reply("❌ Análise incompleta (resposta longa ou imagem ruim). Envie print maximizado/nítido.")
            return
        
        # Pega a legenda e trunca em 50 chars fortes (Impede a API de pesquisar um livro e estourar)
        termo_noticia = message.caption[:50].strip() if message.caption else "Mercado Cripto"
        
        noticias_str = await asyncio.to_thread(buscar_noticias, termo_noticia)
        
        MAX_TENTATIVAS = 3
        texto_gemini = ""
        sucesso_ia = False
        
        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                texto_gemini = await analisar_imagem_com_gemini(image)
                
                # Barragem forte: se depois do max_tokens o Gemini ainda entregar 
                # coisa corrompida maior que o permitido ou a palavra-chave de erro,
                # joga o try fora para avisar de foto errada!
                if len(texto_gemini) > 3700 or "Análise incompleta" in texto_gemini:
                    raise ValueError("Alucinação de OCR longa demais")
                    
                sucesso_ia = True
                break
            except Exception as tr_err:
                logging.error(f"Falha na IA ({tentativa}/3): [{repr(tr_err)}]")
                if tentativa < MAX_TENTATIVAS:
                    await asyncio.sleep(2.0)
                else:
                    await msg_status.delete()
                    await message.reply("❌ Análise incompleta (resposta longa ou imagem ruim). Envie print maximizado/nítido.")
                    return
        
        if not sucesso_ia: return
        
        # Monta Noticias puras, sem imprimir blocos de TITULOS repetidos na ausencia da Chave Serp
        bloco_noticias = ""
        if noticias_str:
            bloco_noticias = f"🗞️ RADAR WEB DE NOTÍCIAS ({termo_noticia.upper()})\n{noticias_str}\n"
        
        # O cabeçalho vem obrigatoriamente logo no comeco da var que agrupa
        linha_tracejada = "_" * 45
        resposta_final = (
            f"⚠️ Análise gerada por IA - Avalie risco antes de operar.\n"
            f"{linha_tracejada}\n\n"
            f"📊 ANALISADOR DE ATIVOS V1.0\n"
            f"👁️ ATIVO BASE: {termo_noticia.upper()}\n\n"
            f"{texto_gemini}\n\n"
            f"{bloco_noticias}"
        )
        
        await msg_status.delete()
        await enviar_resposta_longa(message, resposta_final)
        
    except Exception as e:
        logging.error(f"Travador da foto principal ({user_id}): {repr(e)}")
        await msg_status.delete()
        # Tratamento cirurgico de erro geral curto e conciso:
        await message.reply("❌ Análise incompleta (resposta longa ou imagem ruim). Envie print maximizado/nítido.")

async def main():
    """Boot do Telegram Server Async."""
    logging.info("♻️ Startando Servidor e limpando chamadas atrasadas...")
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("🚀 [ChartAnalyzerBot] Online e Operante! V4.1 (Anti-OCR Spill Block)")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Bot Desconectado Manualmente. Até mais!")
