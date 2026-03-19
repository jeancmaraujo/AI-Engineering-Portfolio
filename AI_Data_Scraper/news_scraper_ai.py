import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURATION PIPELINE
# ==========================================
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"
OUTPUT_FILE = "daily_executive_report.md"

def fetch_tech_news():
    """Realiza o scraping no Google News buscando palavras-chave de alto impacto financeiro."""
    print("🕸️ Iniciando Crawler/Scraper no radar financeiro (Cripto, FED, Trump)...")
    
    # URL mágica: Busca exatamente por essas palavras-chave nos jornais em PT-BR
    url = "https://news.google.com/rss/search?q=Criptomoedas+OR+Bitcoin+OR+FED+OR+Trump+OR+Bovespa&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # O RSS usa estrutura XML, o html.parser do BeautifulSoup lê as tags <item> e <title>
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        
        # Pega as 7 principais notícias do momento sobre esses temas
        for item in soup.find_all('item')[:12]:
            title = item.find('title')
            if title:
                # Limpa o texto para ficar perfeito para a IA
                headlines.append(title.text.strip())
                
        return headlines
    except Exception as e:
        print(f"❌ Falha de Rede ou Scraping Bloqueado: {e}")
        return []

def summarize_with_llm(headlines):
    """Você é um Trader Quantitativo, Analista Macroeconômico Sênior e Especialista em Criptomoedas.
Acabei de fazer o scraping das principais manchetes globais sobre Cripto, FED, Trump e Bolsa de Valores:

{headlines_text}

Sua tarefa analítica (Responda EXCLUSIVAMENTE em Português-BR):
1. **Impacto no Mercado**: Liste as manchetes, definindo uma Tag/Categoria entre colchetes (ex: [Cripto/Solana], [Macroeconomia/FED], [Geopolítica/Trump]). Para cada uma, adicione uma frase curta prevendo se isso é "Bullish" (Alta) ou "Bearish" (Baixa) para os mercados de risco.
2. **Estratégia do Dia (TL;DR)**: Escreva EXATAMENTE 1 parágrafo robusto direcionado a um operador de mesa proprietária. O parágrafo deve resumir o sentimento do mercado hoje e qual deve ser o nível de exposição ao risco.

Formate sua resposta inteiramente em Markdown amigável e profissional.
"""
    print("\n🧠 Injetando manchetes no LLama 3.1 (Automated Market Intelligence)...")
    
    headlines_text = "\n".join([f"- {h}" for h in headlines])
    
    prompt = f"""Você é um Cientista de Dados e Analista de Inteligência de Mercado Sênior.
Acabei de fazer o scraping das 5 principais manchetes globais de tecnologia e ecossistema de dados:

{headlines_text}

Sua tarefa analítica (Responda EXCLUSIVAMENTE em Português-BR):
1. **Categorização**: Liste as mesmas 5 manchetes, definindo uma Tag/Categoria entre colchetes para cada uma (ex: [Mercado], [Inteligência Artificial], [Segurança da Informação], [Política]).
2. **Resumo Executivo (TL;DR)**: Escreva EXATAMENTE 1 parágrafo robusto direcionado ao CTO (Chief Technology Officer) de uma empresa. O parágrafo deve resumir a tendência geral do dia com base nas manchetes para que ele leia em 30 segundos no café da manhã e tome decisões.

Formate sua resposta inteiramente em Markdown amigável e profissional.
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "Erro na Geração Textual do LLama 3.1.")
    except Exception as e:
        print(f"❌ LLM completion failed: {e}")
        return ""

def main():
    print("=" * 60)
    print("📈 PIPELINE INICIADA: AI DATA SCRAPER & MARKET INTELLIGENCE")
    print("=" * 60)
    
    headlines = fetch_tech_news()
    if not headlines:
        print("⚠️ Nenhuma manchete coletada. Verifique sua conexão ou se o DOM do site mudou.")
        return
        
    print("\n📰 [DATA PIPELINE] Manchetes Extraídas com Sucesso:")
    for i, h in enumerate(headlines, 1):
        print(f"  {i}. {h}")
        
    print("-" * 60)
    
    # NLP Summarization Node
    report_content = summarize_with_llm(headlines)
    
    if report_content:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 DAILY EXECUTIVE REPORT - MARKET INTELLIGENCE\n\n{report_content}\n")
            
        print(f"\n✅ Pipeline 100% Concluída!\nO Relatório Diretivo foi gerado, lapidado pela IA e salvo em: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
