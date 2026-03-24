# ChartAnalyzerBot 📈🤖

Este é um bot completo do Telegram escrito em Python (Assíncrono via `aiogram` 3.x) focado na análise técnica e fundamentalista de gráficos financeiros. Ele combina a visão computacional super-avançada do **Google Gemini (gemini-2.0-flash)** para ler os suportes, resistências e indicadores, de mãos dadas com a busca na **SerpAPI (Google News)** para trazer as últimas manchetes do ativo analisado.

## ✨ Funcionalidades
- **Reconhecimento Estrutural**: Detecta RSI, Volume, Médias Móveis, Padrões de Candlestick, Divergências.
- **Análise Técnica Criteriosa**: Traça e relata as primordiais Zonas de Liquidez, Suportes, Resistências.
- **Risk:Reward Otimizado**: Calcula faixas de Entrada Segura, Take-Profit Escalonado e Stop-Loss buscando proteção a violinas (RR base minimamente de 1:3).
- **Radar Fundamentalista**: Escrutina a Web pelo ativo citado (Google News / SerpAPI) e elenca as 3 notícias fortes recentes.
- **Filtro Anti-Flood (Rate Limit)**: Bloqueio estrito de 60 segundos obrigatórios por cliente, com contagem autônoma que blinda o bot de spam, evitando derrubar os limites gratuitos das suas APIs.

## 🚀 Como instalar e rodar (Setup)

### 1. Pré-Requisitos
- Python 3.9 ou versão superior instalado no computador/servidor.
- Um Token de novo Bot Telegram (Fale com o [@BotFather](https://t.me/botfather) e crie um).
- Google Gemini API Key: Peça de graça em [Google AI Studio](https://aistudio.google.com/app/apikey).
- (Opcional) SerpAPI Key: Peça os créditos do Free Tier no [SerpAPI](https://serpapi.com/) para as novidades do mercado.

### 2. Preparando os Motores (Virtual Environment)
Acesse a pasta onde baixou este repositório no seu terminal e instale:

```bash
# 1. Cria a caixa isolada do python
python -m venv venv

# 2. Ativa o ambiente no Windows:
venv\Scripts\activate
# Ou se for no Linux/Mac:
source venv/bin/activate

# 3. Baixa toda tecnologia necessária
pip install -r requirements.txt
```

### 3. Escondendo as Chaves Secretas (`.env`)
Duplique o arquivo `.env.example`, mas no arquivo novo remova o ".example" (Deixe o mome do arquivo APENAS de `.env`). 
Edite como texto e cole suas senhas verdadeiras:

```ini
TELEGRAM_TOKEN=123456789:AABBCcDDeEExemplo...
GEMINI_API_KEY=AIzaxxxSuasLetrasDaAPI...
SERPAPI_KEY=abce123_Sua_API_Serp  # Pode apagar/deixar vazio se preferir operar sem o news scanner
```

### 4. Dando Partida 🏁
Tudo certo com o `.env` e as dependências? Rode o servidor com:
```bash
python main.py
```
> Deverá ver uma mensagem "🚀 [ChartAnalyzerBot] Online e operando no Telegram!" no seu console.

### 5. Utilizando o Bot
- Encontre seu bot criado lá no Telegram e mande um `/start`.
- Faça o envio simples de uma **Foto/Print** limpa do seu gráfico (Bitcoin, Ethereum, PETR4, MiniÍndice).
- Escreva na **LEGENDA DA FOTO** qual é o nome do ativo se quiser a análise de notícias junto (ex: "Solana", "Dólar", "LIXO3").
- Pronto! O robô analisará os pixels, tecerá a matriz de suporte/resitência/entrada e ditará a *Recomendação de Compra ou Venda*. 💰
