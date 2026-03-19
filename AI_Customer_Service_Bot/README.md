# AI Customer Service Agent: Private RAG + Telegram Bot

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Local%20RAG-purple)
![Ollama](https://img.shields.io/badge/LLM-Llama%203.1-orange)

## 📌 Overview
This project showcases an enterprise-grade Customer Service Bot integrated with Telegram, powered entirely by an offline Large Language Model (**Llama 3.1** via Ollama). 

To prevent LLM hallucination (making up incorrect refund policies or shipping times), the architecture utilizes a lightweight **RAG (Retrieval-Augmented Generation)** methodology. The system reads an internal knowledge base (`faq_empresa.txt`) and dynamically engineers prompts to rigorously constrain the AI's reasoning exclusively to the company's factual records.

## 🚀 Features
- **Zero Hallucination Blueprint:** The prompt forcefully prevents the Agent from supplying knowledge outside of the `faq_empresa.txt`.
- **Absolute Data Privacy:** Unlike ChatGPT or OpenAI API implementations, no internal company metrics or user interactions are sent to third parties. Everything runs within local perimeter constraints on port `:11434`.
- **Real-Time Consumer Support:** High asynchronous performance built strictly with `python-telegram-bot` (v20+).
- **Graceful Error Handling:** If the local LLM times out or is offline, users are appropriately redirected to the human support queue instead of receiving raw stack traces.

## 🛠️ Tech Stack
- **Language:** Python
- **Bot Engine:** `python-telegram-bot`
- **Reasoning API:** Local requests to Ollama inference
- **Context Injection:** Raw TXT reading as RAG

## ⚙️ Installation & Setup

1. **Install Ollama**
   - Head over to [ollama.com](https://ollama.com)
   - Install the underlying model:
     ```bash
     ollama run llama3.1
     ```

2. **Clone and Install App Environments**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Your Telegram Bot Token**
   - Search for **@BotFather** on Telegram.
   - Use the command `/newbot` and follow the instructions to generate your API Token.
   - Open `telegram_rag_bot.py` and replace `REPLACE_WITH_YOUR_TELEGRAM_BOT_TOKEN` with your newly generated token.

## 💻 Usage
Ensure you have edited `faq_empresa.txt` to inject your own simulated company data. Once your token is injected, simply execute:

```bash
python telegram_rag_bot.py
```

The bot will begin polling. Open Telegram and send `/start` to your bot. Ask it any policy question regarding shipping or refunds to witness accurate RAG retrieval in real-time.
