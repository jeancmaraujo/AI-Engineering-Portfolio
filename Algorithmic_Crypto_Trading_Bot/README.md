# Algorithmic Crypto Trading Bot

## 🧠 Overview
A highly robust financial automation system built in Python that tracks, measures, and trades cryptocurrency perpetual futures via Telegram. This asynchronous bot continuously monitors dynamic altcoin markets (e.g. BTC, SOL) by aggregating price feeds and executing sophisticated technical indicators (RSI, SMA).

## ⚙️ Architecture & Features
- **Data Integration:** Utilizes the `ccxt` library for high-speed Binance WebSocket/REST connections and calls decentralized API aggregators (Jupiter/Birdeye).
- **Mathematical Indicators:** The backend algorithm calculates custom Relative Strength Index (RSI) periods, Moving Averages, and exponential price movements, leveraging statistical bounds to dictate entry positions.
- **Alert System:** Features a highly resilient `python-telegram-bot` architecture ensuring async, non-blocking delivery of buy/sell signals to end users.
- **Fault-Tolerance:** Includes automated error recovery sweeps and rate-limiting buffers to handle volatile market events safely.

## 🚀 Business Application
Demonstrates advanced capabilities in building reliable financial technology backend services. It highlights practical experience in:
1. Working with high-frequency **financial REST/WebSocket APIs**.
2. Translating complex **mathematical strategies** into deployable Python logic.
3. Developing consumer-facing interactive Telegram AI bots.

## Getting Started
```bash
pip install -r requirements.txt
python bot.py
```
