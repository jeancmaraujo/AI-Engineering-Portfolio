import asyncio
import requests
from bs4 import BeautifulSoup
from x_auto_poster import post_to_x

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

def fetch_trending_ai_news():
    print("🕸️ [SCRAPER] Escaneando a Internet em busca da manchete mais viral do momento sobre IA/Cripto...")
    # Url do Google News já filtrando apenas as tendências quentes (Top stories)
    url = "https://news.google.com/rss/search?q=Inteligência+Artificial+OR+Bitcoin+OR+OpenAI&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pega a primeiríssima manchete quente e devolve o texto
        titulo = soup.find('title')
        if titulo:
             return titulo.text.strip()
    except Exception as e:
        print(f"❌ Erro no scraper: {e}")
        
    return "Bitcoin atinge novos recordes globais enquanto adoção de Inteligência Artificial dispara."

def build_viral_tweet(manchete):
    print(f"🧠 [LLAMA 3.1] Analisando a Manchete: '{manchete}'")
    print("🤖 [LLAMA 3.1] Modelando um Tweet de alto nível...")
    
    prompt = f"""Você é um Engenheiro de IA, Matemático e Investidor Sênior no X/Twitter.
Escreva um ÚNICO post CURTO (máximo 250 caracteres, cerca de 3 frases) reagindo fortemente à seguinte manchete real de agora:
"{manchete}"

Instruções ESTRITAS:
1. Comece com uma constatação técnica ou visionária sobre a notícia.
2. Seja HUMILDE, educativo e inspirador: NÃO diga com arrogância que você "já está rico" ou "ganhando rios de dinheiro". Em vez disso, passe a visão de que "o dinheiro e as enormes assimetrias do mundo hoje estão na mesa para quem decidir se aprofundar no uso de Agentes Locais e Código". Seu papel é incentivar e mostrar o poder do código.
3. Coloque hashtags curtas no final, incluindo OBRIGATORIAMENTE #ClaudeCode e #Python.
4. NUNCA use "Aqui está o seu tweet:", NUNCA use aspas na resposta. Apenas o TEXTO EXATO que vai ser postado no X.
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        tweet = response.json().get("response", "").strip()
        # Higiene do LLM (Garante que não vieram aspas no começo e fim)
        if tweet.startswith('"') and tweet.endswith('"'):
            tweet = tweet[1:-1]
            
        print("\n" + "-"*50)
        print("TWEET GERADO PRONTO PARA DISPARO:")
        print(tweet)
        print("-" * 50 + "\n")
        return tweet
    except Exception as e:
        print(f"❌ Falha de Conexão com Llama Local: {e}")
        return "Agentes Autônomos rodando no meu PC processam o mercado de Cripto enquanto durmo. A automação vai separar os ricos do resto na próxima década. #ClaudeCode #Python #Llama"

async def main():
    print("=" * 60)
    print("🚀 PIPELINE INICIADA: X VIRAL AGENT (AI END-TO-END)")
    print("=" * 60)
    
    # 1. Busca a notícia do Mundo Real (Top 1)
    manchete_quente = fetch_trending_ai_news()
    
    # 2. Usa a IA Local para criar uma opinião genial/polêmica
    tweet_text = build_viral_tweet(manchete_quente)
    
    # 3. Importa e Roda a Função Playwright que vai injetar no X Oficial!
    print("\n⏳ Preparando para lançar no X... Assistindo a automação assumir o teclado...\n")
    await post_to_x(tweet_text)
    
    print("\n🎉 MISSÃO CUMPRIDA! Engajamento autônomo enviado com sucesso!")

def build_night_tweet():
    print("🤖 [LLAMA 3.1] Modelando Relatório Noturno (Build in Public)...")
    
    prompt = f"""Você é um Engenheiro de IA, Matemático e Investidor Sênior no X/Twitter.
Escreva um ÚNICO post CURTO (máximo 250 caracteres, cerca de 3 frases) de FECHAMENTO DE DIA para a noite.

Instruções ESTRITAS:
1. Diga que enquanto os day traders convencionais estão exaustos olhando telas, você já delegou toda essa carga de estresse pro seu Agente Autônomo em Python que vai monitorar o mercado cripto pela madrugada afora.
2. Mantenha seu tom educacional e superior que confia totalmente apenas na matemática e automação.
3. Coloque OBRIGATORIAMENTE no final as hashtags: #BuildInPublic #ClaudeCode #Python.
4. NUNCA use "Aqui está o seu tweet:", nem aspas na resposta. APENAS O TEXTO DO TWEET.
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        tweet = response.json().get("response", "").strip()
        if tweet.startswith('"') and tweet.endswith('"'): tweet = tweet[1:-1]
        print("\n" + "-"*50)
        print("TWEET NOTURNO GERADO PRONTO PARA DISPARO:")
        print(tweet)
        print("-" * 50 + "\n")
        return tweet
    except Exception as e:
        print(f"❌ Falha de Conexão com Llama Local: {e}")
        return "Mais um dia encerrado. Enquanto os day traders tentam prever notícias exaustos, meu Agente em Python assume o comando da Binance pela madrugada afora. Construindo o futuro das finanças dormindo. #BuildInPublic #ClaudeCode #Python"

async def postar_relatorio_da_noite():
    print("=" * 60)
    print("🌙 PIPELINE INICIADA: RELATÓRIO DO FIM DO DIA (20H)")
    print("=" * 60)
    
    tweet_text = build_night_tweet()
    await post_to_x(tweet_text)
    print("\n🎉 MISSÃO DA NOITE CUMPRIDA! O bot pode voltar a dormir.")

if __name__ == "__main__":
    asyncio.run(main())
