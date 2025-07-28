import requests
import os
import time
import hmac
import hashlib
import base64

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(message, secret):
    mac = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

def get_headers(method, path, body=""):
    timestamp = get_timestamp()
    pre_hash = timestamp + method.upper() + path + body
    signature = sign(pre_hash, API_SECRET)
    
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

async def get_portfolio_value():
    try:
        path = "/api/v2/spot/account/assets"
        url = BASE_URL + path
        headers = get_headers("GET", path)
        response = requests.get(url, headers=headers)
        data = response.json()

        coins = data.get("data", [])
        portfolio_lines = []
        total_value = 0.0
        symbols = []

        for coin in coins:
            symbol = coin["coin"].upper()
            available = float(coin.get("available", 0))
            locked = float(coin.get("locked", 0))
            total = available + locked
            if total == 0:
                continue

            price = get_usd_price(symbol)
            value = total * price
            total_value += value
            symbols.append(symbol)
            portfolio_lines.append(f"- {symbol}: {total:.4f} ≈ ${value:.2f}")

        portfolio_lines.append(f"\n💰 *Общая стоимость портфеля*: ${total_value:.2f}")
        return "\n".join(portfolio_lines), symbols

    except Exception as e:
        return f"❌ Ошибка при получении портфеля: {e}", []

def get_usd_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data.get(symbol.lower(), {}).get("usd", 0.0)
    except:
        return 0.0
