import os
import json
import logging
import requests
import pandas as pd
import pandas_ta as ta
import ccxt
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================================================
# Configurações Iniciais e Variáveis Globais
# ==========================================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# 1. Troca do mercado principal para Binance Futures USD-M (PERP)
exchange = ccxt.binanceusdm({'enableRateLimit': True})

# 2, 3 e 7. Símbolos no formato bruto de Futures (ex: BTCUSDT) e endereço real do HYPE
ASSETS = {
    'BTCUSDT': {'type': 'ccxt'},   
    'PAXGUSDT': {'type': 'ccxt'}, 
    'SOLUSDT': {'type': 'ccxt'},
    'HYPEUSDT': {'type': 'birdeye', 'address': '98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g'} 
}

# 4 e 7. Suportes adaptados para as nomenclaturas novas e dados de mercado reais do HYPE
SUPPORTS = {
    'BTCUSDT': (68800, 69500),
    'PAXGUSDT': (4500, 4560),
    'SOLUSDT': (120, 130),
    'HYPEUSDT': (25.0, 32.0)
}

signal_counts = {asset: {'date': str(datetime.now().date()), 'count': 0} for asset in ASSETS}
is_running = True
active_trades = {}

# ==========================================================
# Funções de Aquisição e Exportação do Estado
# ==========================================================
def save_bot_state():
    state = {
        'is_running': is_running,
        'signals': signal_counts,
        'active_trades': active_trades,
        'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open('bot_state.json', 'w') as f:
            json.dump(state, f)
    except Exception as e:
        logger.error(f"Erro ao salvar state: {e}")

def get_current_price(asset, asset_info):
    """6. Auxiliar p/ verificar o preço atual diretamente em mercado Futures com formato bruto."""
    try:
        if asset_info['type'] == 'ccxt':
            try:
                # Fallback preferencial que conversa direto c/ API Rest da Binance para IDs brutos
                res = exchange.fapiPublicGetTickerPrice({'symbol': asset})
                return float(res['price'])
            except Exception:
                # Caso contorne pelo unificado da CCXT
                markets = exchange.load_markets()
                unified_sym = next((s for s, m in markets.items() if m['id'] == asset), asset)
                ticker = exchange.fetch_ticker(unified_sym)
                return ticker['last']
        else:
            url = f"https://public-api.birdeye.so/defi/price?address={asset_info['address']}"
            res = requests.get(url, headers={"X-API-KEY": BIRDEYE_API_KEY}).json()
            return res['data']['value']
    except Exception as e:
        logger.error(f"Erro Price/Ticker [{asset}]: {e}")
        return None

def get_funding_rate(asset):
    """5. Lógica FAPI que aceita requisição direta de 'BTCUSDT' no modelo binanceusdm."""
    if ASSETS[asset]['type'] != 'ccxt':
        return -1.0 
    try:
        res = exchange.fapiPublicGetPremiumIndex({'symbol': asset})
        if isinstance(res, list):
            res = res[0]  # Dependendo da versão, binance envia resposta empacotada
        return float(res['lastFundingRate'])
    except Exception as e:
        logger.error(f"Erro Funding Rate {asset}: {e}")
        return 0.0

def get_binance_ohlcv(symbol, timeframe, limit=100):
    """Proteção com conversão de symbol (Mapeia BTCUSDT -> BTC/USDT:USDT p/ o fetch_ohlcv padrão)"""
    try:
        markets = exchange.load_markets()
        ccxt_symbol = next((s for s, m in markets.items() if m['id'] == symbol), symbol)
        
        ohlcv = exchange.fetch_ohlcv(ccxt_symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Erro Binance OHLCV [{symbol}]: {e}")
        return None

def get_birdeye_ohlcv(address, timeframe, limit=100):
    type_map = {'15m': '15m', '1h': '1H', '4h': '4H', '12h': '12H'}
    tf = type_map.get(timeframe, '15m')
    url = f"https://public-api.birdeye.so/defi/ohlcv?address={address}&type={tf}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY, "accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get('success'):
            items = data['data']['items'][-limit:]
            df = pd.DataFrame(items)
            df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}, inplace=True)
            return df
        return None
    except Exception:
        return None

def calculate_indicators(df):
    if df is None or len(df) < 55:
        return None
    df['rsi_14'] = ta.rsi(df['close'], length=14)
    df['ma21'] = ta.sma(df['close'], length=21)
    df['ma35'] = ta.sma(df['close'], length=35)
    df['ma50'] = ta.sma(df['close'], length=50)
    df['vol_sma20'] = ta.sma(df['volume'], length=20)
    return df

# ==========================================================
# Motor de Análise Base e Regras
# ==========================================================
def analyze_asset(asset_name, asset_info):
    # Trava do Funding Rate (< 0 apenas)
    funding_rate = get_funding_rate(asset_name)
    if funding_rate >= 0 and asset_info['type'] == 'ccxt':
        return None

    symbol = asset_name
    if asset_info['type'] == 'ccxt':
        df_long = get_binance_ohlcv(symbol, '4h')
        df_short = get_binance_ohlcv(symbol, '1h')
    else:
        df_long = get_birdeye_ohlcv(asset_info['address'], '4h')
        df_short = get_birdeye_ohlcv(asset_info['address'], '1h')
        
    df_long = calculate_indicators(df_long)
    df_short = calculate_indicators(df_short)
    
    if df_long is None or df_short is None: return None
        
    last_long = df_long.iloc[-1]
    last_short, prev_short = df_short.iloc[-1], df_short.iloc[-2]
    
    # Conjunto de 6 Regras Rígidas
    if last_long['rsi_14'] >= 30: return None
    if not (prev_short['rsi_14'] <= 35 and last_short['rsi_14'] > 35): return None
    
    ma21_crossed = (prev_short['ma21'] <= prev_short['ma35']) and (last_short['ma21'] > last_short['ma35'])
    both_above = (last_short['ma21'] > last_short['ma50']) and (last_short['ma35'] > last_short['ma50'])
    if not (ma21_crossed and both_above): return None
        
    current_price = last_short['close']
    sup_min, sup_max = SUPPORTS[asset_name]
    if current_price < sup_min or current_price > (sup_max * 1.03): return None
    if last_short['volume'] <= last_short['vol_sma20']: return None
        
    body = last_short['close'] - last_short['open']
    if body <= 0: return None
    candle_range = last_short['high'] - last_short['low']
    if candle_range == 0 or (body / candle_range) < 0.6: return None
        
    stop_loss = sup_min * 0.985
    risk = current_price - stop_loss
    
    return {
        'asset': asset_name,
        'price': current_price,
        'rsi_4h': last_long['rsi_14'],
        'support': f"${sup_min} - ${sup_max}",
        'stop_loss': stop_loss,
        'alvo1': current_price + (risk * 3),
        'alvo2': current_price + (risk * 5),
        'funding_rate': funding_rate
    }

# ==========================================================
# Loop de 5 Minutos (Job Queue)
# ==========================================================
async def check_signals(context: ContextTypes.DEFAULT_TYPE):
    global is_running
    today_str = str(datetime.now().date())
    
    # 1. Gerenciamento de Posições (Saídas e Trailing Stop)
    for asset, trade in list(active_trades.items()):
        current_price = get_current_price(asset, ASSETS[asset])
        if not current_price: continue
        
        # Otimiza o stop loss na subida
        if current_price > trade['highest_price']:
            trade['highest_price'] = current_price
            novo_stop = current_price * 0.99
            if novo_stop > trade['stop_loss']:
                trade['stop_loss'] = novo_stop
        
        if current_price >= trade['alvo1'] or current_price >= trade['alvo2']:
            lucro_pct = ((current_price - trade['entry_price']) / trade['entry_price']) * 100
            msg = f"🟡 *SINAL DE SAÍDA* - Lucro {lucro_pct:.2f}%\n"
            msg += f"Ativo: {asset}\nSaída: ${current_price:.4f}"
            await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            del active_trades[asset]
            continue
            
        if current_price <= trade['stop_loss']:
            loss_pct = ((trade['entry_price'] - current_price) / trade['entry_price']) * 100
            msg = f"🔴 *STOP LOSS ATINGIDO*\n"
            msg += f"Ativo: {asset}\nSaída: ${current_price:.4f}\nPCP: -{loss_pct:.2f}%"
            await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            del active_trades[asset]
            continue

    if not is_running:
        save_bot_state()
        return
        
    # 2. Rastreio de Entradas
    for asset, info in ASSETS.items():
        if signal_counts[asset]['date'] != today_str:
            signal_counts[asset] = {'date': today_str, 'count': 0}
            
        if signal_counts[asset]['count'] >= 2 or asset in active_trades:
            continue
            
        signal = analyze_asset(asset, info)
        
        if signal:
            signal_counts[asset]['count'] += 1
            
            active_trades[asset] = {
                'entry_price': signal['price'],
                'highest_price': signal['price'],
                'stop_loss': signal['stop_loss'],
                'alvo1': signal['alvo1'],
                'alvo2': signal['alvo2']
            }
            
            msg = f"🟢 *SINAL DE ENTRADA* - {signal['asset']}\n"
            msg += f"Preço: ${signal['price']:.4f}\n"
            if signal['funding_rate'] != -1.0:
                msg += f"Funding Rate: *{signal['funding_rate']:.4%}*\n"
            msg += f"RSI 4h: {signal['rsi_4h']:.1f} (oversold)\n"
            msg += f"Suporte: {signal['support']}\n"
            msg += f"Stop-loss: ${signal['stop_loss']:.4f}\n"
            msg += f"Alvo 1: ${signal['alvo1']:.4f} / Alvo 2: ${signal['alvo2']:.4f}\n"
            msg += "Risco-recompensa: 1:3+"
            
            await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
    save_bot_state()

# ==========================================================
# Comandos
# ==========================================================
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"📊 *Status do Bot*\nAtivo: {'Sim ✅' if is_running else 'Não ❌'}\n\n"
    msg += "*Sinais gerados hoje (Máx 2):*\n"
    for asset, data in signal_counts.items():
        msg += f"🔸 {asset}: {data['count']}/2\n"
        
    msg += "\n*Posições Abertas:*\n"
    if active_trades:
        for ast, t in active_trades.items():
            msg += f"📈 {ast} - Entrada: ${t['entry_price']:.2f}\n"
    else:
        msg += "Nenhuma.\n"
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    is_running = not is_running
    state = "pausado 🛑" if not is_running else "reativado ▶️"
    save_bot_state()
    await update.message.reply_text(f"Bot {state} com sucesso!")

async def backtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Iniciando backtest vetorial dos últimos 30 dias na Binance (Futures). Aguarde...")
    
    df = get_binance_ohlcv('BTCUSDT', '1h', limit=720) 
    if df is None:
        return await update.message.reply_text("Erro ao puxar dados da Binance Futures.")
        
    df = calculate_indicators(df)
    
    total_signals = 0
    wins = 0
    drawdown = 0.0
    
    for i in range(50, len(df)-1):
        if df['rsi_14'].iloc[i-1] <= 35 and df['rsi_14'].iloc[i] > 35:
            if df['volume'].iloc[i] > df['vol_sma20'].iloc[i]:
                total_signals += 1
                close_futuro = df['close'].iloc[i+1:].max()
                low_futuro = df['low'].iloc[i+1:].min()
                entrada = df['close'].iloc[i]
                
                stop = entrada * 0.985
                alvo = entrada + ((entrada - stop)*3)
                
                if close_futuro >= alvo: wins += 1
                
                dd_atual = (entrada - low_futuro)/entrada * 100
                if dd_atual > drawdown: drawdown = dd_atual
                
    win_rate = (wins / total_signals * 100) if total_signals > 0 else 0
    lucro_estimado_pct = (wins * 4.5) - ((total_signals - wins) * 1.5)
    
    msg = f"📊 *Resultados Backtest 30 Dias (BTCUSDT PERP)*\n\n"
    msg += f"Sinais encontrados: {total_signals}\n"
    msg += f"Win Rate Estimado: {win_rate:.1f}%\n"
    msg += f"Lucro Total (1:3): +{lucro_estimado_pct:.2f}%\n"
    msg += f"Drawdown Máximo: -{drawdown:.2f}%"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

# ==========================================================
# Inicializador Principal
# ==========================================================
def main():
    if not TOKEN or not CHAT_ID: return
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("backtest", backtest_command))
    
    save_bot_state() 
    job_queue = app.job_queue
    job_queue.run_repeating(check_signals, interval=300, first=5)
    
    logger.info("Bot Online: Motor Binance-USDM Futures + HYPE Real + Endpoints Nativos Ativados.")
    app.run_polling()

if __name__ == '__main__':
    main()
