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

SEEN_TOKENS = set()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error Telegram: {e}")

def scan_tokens():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return
            
        profiles = res.json()
        sol_tokens = [p for p in profiles if p.get('chainId') == 'solana']
        
        for item in sol_tokens[:10]:
            token_address = item.get('tokenAddress')
            if not token_address or token_address in SEEN_TOKENS:
                continue

            pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            pair_res = requests.get(pair_url, timeout=5)
            if pair_res.status_code != 200:
                continue
                
            data = pair_res.json()
            if not data.get('pairs'):
                continue

            pair = data['pairs'][0]
            buys_5m = pair.get('txns', {}).get('m5', {}).get('buys', 0)
            buys_per_min = buys_5m / 5.0
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            symbol = pair.get('baseToken', {}).get('symbol', 'TOKEN')
            price = pair.get('priceUsd', '0')
            fdv = pair.get('fdv', 0)

            if buys_per_min >= MIN_BUYS_PER_MINUTE and liquidity >= MIN_LIQUIDITY_USD:
                alert_text = (
                    f"🚨 *¡NUEVO TOKEN EN SOLANA!* 🚨\n\n"
                    f"🪙 *Token:* `${symbol}`\n"
                    f"🔥 *Velocidad:* `{buys_per_min:.1f}` compras/min\n"
                    f"💧 *Liquidez:* `${liquidity:,.0f}` USD\n"
                    f"🧢 *Market Cap:* `${fdv:,.0f}` USD\n"
                    f"💵 *Precio:* `${price}`\n\n"
                    f"📍 *Contrato:* `{token_address}`\n\n"
                    f"🔗 [Ver en GMGN](https://gmgn.ai/sol/token/{token_address})\n"
                    f"🤖 [Comprar en Trojan](https://t.me/solana_trojanbot?start=r-user-{token_address})"
                )
                send_telegram_alert(alert_text)
                SEEN_TOKENS.add(token_address)
                
    except Exception as e:
        print(f"Error escaneando: {e}")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    send_telegram_alert("🟢 *Escáner Activo*: Monitoreando nuevos tokens en Solana.")
    
    while True:
        scan_tokens()
        time.sleep(CHECK_INTERVAL_SEC)
