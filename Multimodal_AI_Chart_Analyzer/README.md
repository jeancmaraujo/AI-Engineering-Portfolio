# Multimodal AI Chart Analyzer 📈🤖
*Status: Python, Computer Vision, Gemini AI, RAG*

### 📌 Overview
A cutting-edge visual intelligence Agent that lives inside Telegram. The bot harnesses the **Google Gemini Vision API** to read, process, and analyze complex candlestick trading charts uploaded by the user, combining visual AI with real-time web search (SerpAPI).

### 🚀 Features
- **Computer Vision Pipeline:** Intercepts image blobs via Telegram, normalizes the aspect ratio utilizing `Pillow (PIL)`, and queues the data chunking process for the Vision Model.
- **Technical & Fundamental Analysis:** Deciphers visual trendlines (Support/Resistance) and synchronously cross-references findings using `SerpAPI` to scan live news.
- **Strict Rate Limiting:** Built-in 60-second autonomous cooldowns to prevent spamming and protect free-tier API limits.

### 🛠️ Tech Stack
- **Language:** Python
- **Vision AI:** Google Gemini 2.0 Flash
- **Search Integration:** SerpAPI (Google News)
- **Image Processing:** Pillow

### ⚙️ Installation & Setup
1. **Clone & Install:** `pip install -r requirements.txt`
2. **Environment Variables:** Create a [.env](cci:7://file:///c:/Users/Jean/Automacoes_X/bot_trade_perp/.env:0:0-0:0) file and insert your API keys:
   `TELEGRAM_TOKEN=...`
   `GEMINI_API_KEY=...`
   `SERPAPI_KEY=...`

### 💻 Usage
Give the exact command below to wake up the server:
```bash
python main.py
