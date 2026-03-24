import json
import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: #ffffff; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .badge-green { background: #4caf50; padding: 5px 10px; border-radius: 5px; font-weight: bold;}
        .badge-red { background: #f44336; padding: 5px 10px; border-radius: 5px; font-weight: bold;}
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; }
        th { background-color: #2c2c2c; }
    </style>
</head>
<body>
    <h1>🤖 Dashboard - Telegram Bot</h1>
    
    <div class="card">
        <h2>Bot Status: 
            {% if state.is_running %}
                <span class="badge-green">ONLINE ✅</span>
            {% else %}
                <span class="badge-red">PAUSADO ❌</span>
            {% endif %}
        </h2>
        <p>Última atualização: {{ state.last_update }}</p>
        <p><em>Utilize os comandos /status e /stop via Telegram.</em></p>
    </div>

    <div class="card">
        <h2>🔥 Posições Abertas (Active Trades)</h2>
        {% if state.active_trades %}
        <table>
            <tr>
                <th>Ativo</th>
                <th>Preço de Entrada</th>
                <th>Stop Loss (Trailing Atual)</th>
                <th>Alvo Primário</th>
            </tr>
            {% for asset, data in state.active_trades.items() %}
            <tr>
                <td><strong>{{ asset }}</strong></td>
                <td>${{ "{:,.2f}".format(data.entry_price) }}</td>
                <td style="color:#ff9800">${{ "{:,.2f}".format(data.stop_loss) }}</td>
                <td style="color:#4caf50">${{ "{:,.2f}".format(data.alvo1) }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p style="color: #999;">Nenhuma posição aberta no momento.</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>📊 Contagem de Sinais Hoje</h2>
        <ul>
            {% for asset, data in state.signals.items() %}
                <li><strong>{{ asset }}</strong>: {{ data.count }} / 2 chamadas max</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

def load_bot_state():
    try:
        if os.path.exists('bot_state.json'):
            with open('bot_state.json', 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {'is_running': False, 'active_trades': {}, 'signals': {}, 'last_update': 'Desconhecido'}

@app.route('/')
def dashboard():
    state = load_bot_state()
    return render_template_string(HTML_TEMPLATE, state=state)

if __name__ == '__main__':
    # Roda o dashboard Web no localhost 
    app.run(host='0.0.0.0', port=5000, debug=False)
