import os
import time
import hmac
import hashlib
import requests
import base64

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_request(timestamp, method, request_path, body=""):
    pre_hash = f"{timestamp}{method}{request_path}{body}"
    secret_bytes = API_SECRET.encode()
    message = pre_hash.encode()
    signature = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()
    return signature

def get_headers(method, request_path, body=""):
    timestamp = get_timestamp()
    signature = sign_request(timestamp, method, request_path, body)
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

def get_usd_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        res = requests.get(url)
        return res.json().get(symbol.lower(), {}).get("usd", 0.0)
    except:
        return 0.0

async def get_portfolio_value():
    try:
        endpoint = "/api/v2/spot/account/assets"
        url = BASE_URL + endpoint
        headers = get_headers("GET", endpoint)

        print("📡 Requesting Bitget portfolio with headers:", headers)
        res = requests.get(url, headers=headers)
        print("📥 Bitget API response:", res.status_code, res.text)

        data = res.json()
        coins = data.get("data", None)

        if not coins:
            raise ValueError("Bitget API не вернул данные по портфелю")

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
        import logging
        logging.exception("Ошибка при получении портфеля: %s", e)
        return "Ошибка при получении портфеля", []
