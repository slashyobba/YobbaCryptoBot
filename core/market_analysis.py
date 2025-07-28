# core/market_analysis.py
import requests
from datetime import datetime, timedelta
import pytz

COINGECKO_API = "https://api.coingecko.com/api/v3"

def fetch_top_coins(limit=30):
    url = f"{COINGECKO_API}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_coin_details(coin_id):
    url = f"{COINGECKO_API}/coins/{coin_id}"
    response = requests.get(url)
    return response.json()

def is_new_coin(coin_data, threshold_days=90):
    if 'genesis_date' in coin_data and coin_data['genesis_date']:
        try:
            coin_date = datetime.strptime(coin_data['genesis_date'], "%Y-%m-%d")
            return datetime.now() - coin_date < timedelta(days=threshold_days)
        except Exception:
            return False
    return False

def analyze_market(user_symbols):
    top_coins = fetch_top_coins(limit=30)
    report_lines = ["📊 *Обзор крипторынка (ТОП-30)*\n"]

    user_symbols_set = set(symbol.lower() for symbol in user_symbols)

    for coin in top_coins:
        name = coin["name"]
        symbol = coin["symbol"].upper()
        price = coin["current_price"]
        change = coin["price_change_percentage_24h"]
        coin_id = coin["id"]

        details = fetch_coin_details(coin_id)
        is_new = is_new_coin(details)

        line = f"*{name}* ({symbol}): ${price:.2f} ({change:+.2f}%)"
        if is_new:
            line += " 🔥 _Новинка!_"

        report_lines.append(line)

    # Добавляем отсутствующие в ТОП-30 пользовательские монеты
    missing = user_symbols_set - set(c['symbol'].lower() for c in top_coins)
    if missing:
        report_lines.append("\n📌 *Дополнительно: Ваши монеты вне ТОП-30*")
        for symbol in missing:
            url = f"{COINGECKO_API}/coins/{symbol.lower()}"
            resp = requests.get(url)
            if resp.status_code != 200:
                report_lines.append(f"- {symbol.upper()}: данные не найдены.")
                continue

            coin = resp.json()
            market = coin.get("market_data", {})
            name = coin.get("name", symbol.upper())
            price = market.get("current_price", {}).get("usd", "?")
            change = market.get("price_change_percentage_24h", "?")
            is_new = is_new_coin(coin)

            line = f"*{name}* ({symbol.upper()}): ${price} ({change:+.2f}%)"
            if is_new:
                line += " 🔥 _Новинка!_"
            report_lines.append(line)

    return "\n".join(report_lines)
