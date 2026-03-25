import os
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Importa o Módulo de Publicação no X que construímos hoje
from x_auto_poster import post_to_x

# O Token agora  é puxado do arquivo .env secreto! O GitHub nunca vai ver.
TOKEN = os.getenv("TELEGRAM_OMNI_TOKEN")
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

# --- MÓDULO 1: EXTRAÇÃO DE DADOS (Scraper) ---
async def extrair_texto_da_url(url):
    print(f"🌐 [SCRAPER] Analisando o Link: {url}")
    try:
        # Finge ser um navegador real para não ser bloqueado por sites
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Coleta Título e Parágrafos básicos
                title = soup.title.string if soup.title else ""
                paragraphs = soup.find_all('p')
                # Pega apenas os 5 primeiros parágrafos para o Llama 3 não estourar a memória
                text = " ".join([p.text for p in paragraphs[:5]]) 
                
                if len(text) < 10:
                    return None
                
                return f"Título do Artigo: {title}\nConteúdo: {text}"
    except Exception as e:
        print(f"❌ Falha no Scraper de URL: {e}")
        return None

# --- MÓDULO 2: MODELAGEM COM LLAMA 3 ---
async def gerar_tweet_do_texto(conteudo):
    print("🧠 [LLAMA 3.1] Convertendo o artigo em Engenharia de Conteúdo Viral para o X...")
    
    prompt = f"""Você é o Agente 0xMDR. O seu criador te enviou o núcleo de uma notícia:
"{conteudo}"

Sua missão: Escreva um ÚNICO post CURTO para o X (máximo 250 caracteres) sobre isso.
Instruções OBRIGATÓRIAS:
1. Comece de forma instigante. Mostre como essa notícia afeta o mercado cripto, desenvolvedores ou inteligência artificial.
2. Foque num tom de Engenheiro Sênior, analítico e imparcial.
3. Finalize SEMPRE com as tags: #0xMDR #ClaudeCode #Python.
4. NUNCA use aspas. Responda APENAS O TEXTO EXATO QUE SERÁ POSTADO, nada de "Aqui está".
"""
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    
    # Executa a requisição síncrona numa thread separada pra não travar o Telegram
    try:
        response = await asyncio.to_thread(requests.post, OLLAMA_API_URL, json=payload, timeout=60)
        tweet = response.json().get("response", "").strip()
        if tweet.startswith('"') and tweet.endswith('"'): 
            tweet = tweet[1:-1]
        return tweet
    except Exception as e:
        print(f"❌ Falha de Conexão com Llama Local: {e}")
        return None


# --- MÓDULO 3: INTEGRAÇÃO TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 **Agente Omnichannel 0xMDR Online!**\n\n"
        "Me envie o **URL/Link** de uma notícia ou artigo Tech.\n"
        "Eu vou vasculhar o conteúdo do site, passar no cérebro da nossa I.A Local, "
        "gerar um texto opinativo, e disparar pro Playwright postar no seu Twitter Imediatamente."
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recebido = update.message.text
    print(f"\n💬 [TELEGRAM] Comando recebido de @{update.effective_user.username}: {texto_recebido}")
    
    # Checa se é um Link ou um Texto Livre
    if not texto_recebido.startswith("http"):
        # Se não for Link, ele processa a mensagem diretamente como Texto Livre! (Muito flexível)
        await update.message.reply_text("🔄 Isso não é um link, mas eu vou criar e postar um Tweet com base exata nesse texto que você me mandou...")
        conteudo = texto_recebido
    else:
        await update.message.reply_text("⏳ Recebi o Link. \n1️⃣ Ativando Scraper para invadir o site e ler o conteúdo...")
        conteudo = await extrair_texto_da_url(texto_recebido)
        
        if not conteudo:
            await update.message.reply_text("❌ Bloqueio Detectado. O site barrou nossa leitura do robô. Tente me mandar um texto copiado (Ctrl+C Ctrl+V) do site em vez do link.")
            return

    await update.message.reply_text("🧠 Leitura Extraída! \n2️⃣ Injetando dados no Llama 3 local para redigir a tese...")
    tweet_gerado = await gerar_tweet_do_texto(conteudo)
    
    if not tweet_gerado:
        await update.message.reply_text("❌ Ocorreu um erro ao falar com o Ollama (Ele está aberto no PC?)")
        return
        
    await update.message.reply_text(f"📝 **Tweet Gerado pelo Agente:**\n\n{tweet_gerado}\n\n🤖 3️⃣ Ligando motor Playwright para postar automaticamente...")
    
    try:
        await post_to_x(tweet_gerado)
        await update.message.reply_text("✅ SUCESSO ABSOLUTO! O Playwright finalizou a postagem no seu perfil do X.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro na ponte Playwright -> X: {e}")

def main():
    print("==============================================")
    print("🤖 SERVIDOR INICIALIZADO: 0xMDR AGENT (v1.0)")
    print("==============================================")
    
    if TOKEN == "COLOQUE_SEU_TOKEN_AQUI":
        print("⚠️ VOCÊ ESQUECEU DE COLOCAR O TOKEN DO TELEGRAM!")
        return

    # Usamos Request HTTP Customizado para estabilidade do Python-Telegram-Bot com event_loops assíncronos
    app = Application.builder().token(TOKEN).build()
    
    # Manipuladores (Rotas) do Celular
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagem))
    
    print("📡 Escutando Sinais do seu celular no Telegram...\n")
    app.run_polling()

if __name__ == "__main__":
    main()
