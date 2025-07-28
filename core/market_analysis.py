import requests
import datetime

# Получаем список топ-30 монет
def get_top_30_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 30,
        "page": 1,
        "sparkline": "false"
    }
    response = requests.get(url, params=params)
    return response.json()

# Проверяем: новая ли монета (вышла < 3 месяцев назад)
def is_new_coin(launch_date):
    try:
        date = datetime.datetime.strptime(launch_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        return (datetime.datetime.utcnow() - date).days <= 90
    except:
        return False

# Анализ монеты
def analyze_coin(coin):
    price_change = coin.get("price_change_percentage_24h", 0)
    volume_change = coin.get("total_volume", 0)

    recommendation = ""
    if price_change > 10:
        recommendation = "🚀 Растёт — возможно, стоит докупить"
    elif price_change < -10:
        recommendation = "📉 Снижается — возможно, время выйти"
    else:
        recommendation = "🤏 Без резких движений"

    if is_new_coin(coin.get("ath_date", "")):
        recommendation += " 🆕 Новинка"

    return recommendation

# Основная функция анализа
async def get_market_summary(user_portfolio_symbols=None):
    coins = get_top_30_coins()
    user_portfolio_symbols = user_portfolio_symbols or []

    summary = "*📊 Рыночный анализ (топ-30):*\n"
    for coin in coins:
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", "")
        price = coin.get("current_price", 0)
        price_change = coin.get("price_change_percentage_24h", 0)
        recommendation = analyze_coin(coin)

        summary += f"\n*{name}* ({symbol}) — ${price:.2f} ({price_change:+.2f}%)\n{recommendation}\n"

    # Отдельный блок по пользовательским монетам
    if user_portfolio_symbols:
        summary += "\n\n*🧾 Монеты из портфеля:*\n"
        all_symbols = [coin["symbol"].upper() for coin in coins]
        for symbol in user_portfolio_symbols:
            if symbol.upper() not in all_symbols:
                try:
                    response = requests.get(f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}")
                    data = response.json()
                    name = data["name"]
                    price = data["market_data"]["current_price"]["usd"]
                    price_change = data["market_data"]["price_change_percentage_24h"]
                    summary += f"\n*{name}* ({symbol.upper()}) — ${price:.2f} ({price_change:+.2f}%)"
                    if is_new_coin(data.get("genesis_date", "")):
                        summary += " 🆕 Новинка"
                    summary += "\n"
                except:
                    summary += f"\n*{symbol.upper()}* — не удалось загрузить данные\n"

    return summary
