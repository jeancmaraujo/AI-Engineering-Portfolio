import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# CONFIGURATION
# ==========================================
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"
FAQ_FILE = "faq_empresa.txt"

# Insert your Telegram Bot token here (From BotFather)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")

def load_knowledge_base():
    """Loads the local text file explicitly used for Simple RAG indexing."""
    text_data = ""
    try:
        with open(FAQ_FILE, 'r', encoding='utf-8') as f:
            text_data = f.read()
    except Exception as e:
        print(f"Error loading {FAQ_FILE}: {e}")
    return text_data

KNOWLEDGE_BASE = load_knowledge_base()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a friendly welcome message when the user issues /start."""
    welcome_text = "Olá! 👋 Sou o Assistente IA da *Tech Solutions*.\n\nComo posso ajudar com o seu pedido hoje? (Tire dúvidas sobre fretes, reembolsos ou horários!)"
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Intercepts user text, injects RAG Context, and routes to Local Llama 3.1"""
    user_query = update.message.text
    
    # RAG PROMPT ENGINEERING: Forcing the LLM to strictly adhere to internal policies
    prompt = f"""You are a polite, helpful AI Customer Support Agent for a Brazilian e-commerce company named Tech Solutions.
Your exact name is "TechBot".
You MUST answer the user's question EXCLUSIVELY using the information from the 'Company Knowledge Base' provided below. 
If the user asks something completely outside the knowledge base, politely inform them that you do not have that information and redirect them to their human support channel: suporte@techsolutions.com.br.
Do NOT invent details, hallucinate shipping times, or make up numbers.
Always answer in standard Portuguese (pt-BR).

Company Knowledge Base:
\"\"\"
{KNOWLEDGE_BASE}
\"\"\"

User Question: {user_query}
TechBot Agent Response:"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # Visual feedback on Telegram to show the bot is "Typing..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        
        # Send to isolated local execution environment
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=45)
        response.raise_for_status()
        
        ai_response = response.json().get("response", "Desculpe, estou com alguma instabilidade no meu cérebro neural.")
        
        # Dispatch final response back to user
        await update.message.reply_text(ai_response.strip())
        
    except requests.exceptions.RequestException as e:
        print(f"LLM Connection Error: {e}")
        error_msg = "Desculpe, nosso servidor local de IA está em manutenção no momento. Tente novamente em breve."
        await update.message.reply_text(error_msg)
    except Exception as e:
        print(f"Unexpected error: {e}")

def main() -> None:
    print("=" * 60)
    print("🤖 STARTING LOCAL NLP RAG AGENT (PYTHON-TELEGRAM-BOT)")
    print("=" * 60)
    
    if TELEGRAM_BOT_TOKEN == "REPLACE_WITH_YOUR_TELEGRAM_BOT_TOKEN":
        print("⚠️ ACTION REQUIRED: You must set your TELEGRAM_BOT_TOKEN in the script.")
        print("1. Talk to @BotFather on Telegram")
        print("2. Create a new bot and copy the API Token")
        print("3. Paste the token into `telegram_rag_bot.py` or set it as an env var.")
        return
        
    if not KNOWLEDGE_BASE.strip():
        print("⚠️ ERROR: The faq_empresa.txt file is empty or missing. RAG context failed.")
        
    # Start the robust Application builder provided by PTB v20+
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Agent is now polling securely. Awaiting messages... (Press Ctrl+C to stop)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
