import json
import logging
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TelegramBot')

class TelegramReporter:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        # Novo diretorio de saida apos refatoracao de scraping
        self.input_file = os.path.join(os.path.dirname(__file__), "time_consenso.json")
        self.bot = Bot(token=self.bot_token)

    def load_data(self):
        if not os.path.exists(self.input_file):
            logger.error(f"Arquivo de consenso {self.input_file} ausente. Rode o consensus_engine.py primeiro.")
            return None
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_html_card(self, data):
        titulares = data.get("titulares", [])
        capitao = data.get("capitao", {})
        
        msg = "🏆 <b>CARTOLA AI - A INTELIGÊNCIA DA WEB</b> 🏆\n"
        msg += "<i>🤖 Big Data: Escala10 + Twitter + Sofascore</i>\n\n"
        
        msg += f"👑 <b>Capitão Unânime (O Consenso):</b> <b>{capitao.get('nome')}</b>\n\n"
        
        msg += "🛡️ <b>ESCALAÇÃO BLINDADA</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        
        for t in titulares:
            nome = t.get('nome', 'N/A')
            pos = str(t.get('posicao', '')).upper()
            clube = t.get('clube', 'N/A')
            fontes = t.get('tracking_fontes', '')
            score = t.get('score_consenso', 0.0)
            
            is_cap = "👑" if nome == capitao.get('nome') else "✅"
            msg += f"<b>{pos}</b>: {nome} | <i>{clube}</i> {is_cap}\n"
            msg += f"  ↳ <i>{fontes}</i> [Power: {score}]\n\n"
            
        msg += "🔮 <i>As vozes de quem mais estuda o game. Sem achismos isolados.</i>"
        return msg

    async def send_report(self):
        data = self.load_data()
        if not data: return
        
        html = self.create_html_card(data)
        if not self.bot_token: 
            logger.warning("Token Ausente.")
            return
            
        try:
            logger.info("Disparando envio Web Consensus via Telegram...")
            await self.bot.send_message(chat_id=self.chat_id, text=html, parse_mode=ParseMode.HTML)
            logger.info("Envio bem sucessido para o canal Premium do Telegram.")
        except Exception as e:
            logger.error(f"Falha de envio: {e}")

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_AQUI")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "MEU_CHAT_ID")
    
    if os.name == 'nt': 
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    reporter = TelegramReporter(bot_token=TOKEN, chat_id=CHAT_ID)
    asyncio.run(reporter.send_report())
