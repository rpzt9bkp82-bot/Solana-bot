import os
import requests
import time
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot activo 24/7"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

TELEGRAM_BOT_TOKEN = "8638035156:AAFyQrvgr9Yu1GN5rM7JkmA_XicAGf1-UaM"
TELEGRAM_CHAT_ID = "5674576418"

MIN_BUYS_PER_MINUTE = 30
MIN_LIQUIDITY_USD = 10000
CHECK_INTERVAL_SEC = 10

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

def scanner_loop():
    # Mensaje de arranque para confirmar que está vivo en Telegram
    send_telegram_alert("🟢 *Escáner Activo*: Monitoreando nuevos tokens en Solana (Filtros: 30+ buys/min, $10k+ Liq).")
    
    while True:
        try:
            # Aquí irá tu lógica de escaneo de tokens
            pass
        except Exception as e:
            print(f"Error en el escáner: {e}")
        time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    # Arranca el escáner en segundo plano
    t = Thread(target=scanner_loop)
    t.daemon = True
    t.start()
    
    # Arranca el servidor web para Railway
    run_web_server()
