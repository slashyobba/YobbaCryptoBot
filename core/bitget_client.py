import requests
import os

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")

def get_headers():
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": "",
        "ACCESS-TIMESTAMP": "",
        "ACCESS-PASSPHRASE": "",
        "Content-Type": "application/json"
    }

async def get_portfolio_value():
    try:
        url = "https://api.bitget.com/api/v2/spot/account/assets"
        response = requests.get(url, headers=get_headers())
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
        return "Ошибка при получении портфеля", []

def get_usd_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data.get(symbol.lower(), {}).get("usd", 0.0)
    except:
        return 0.0
