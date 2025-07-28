import requests

COINGECKO_API = "https://api.coingecko.com/api/v3"

async def get_market_summary(portfolio_symbols=None):
    try:
        portfolio_symbols = [s.upper() for s in (portfolio_symbols or [])]

        coins = requests.get(
            f"{COINGECKO_API}/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 30, "page": 1}
        ).json()

        output = {
            "📈 Растущие монеты": [],
            "📉 Падающие монеты": [],
            "⏸️ Стабильные монеты": [],
            "🆕 Рекомендации (монеты вне портфеля)": []
        }

        for coin in coins:
            symbol = coin["symbol"].upper()
            name = coin["name"]
            price = coin.get("current_price", 0)
            change = coin.get("price_change_percentage_24h", 0) or 0
            in_portfolio = symbol in portfolio_symbols
            signal = ""

            # Сигналы
            if change >= 2:
                signal = "🟢 *Покупать*"
                output["📈 Растущие монеты"].append(f"{symbol}: ${price:.2f} ({change:+.2f}%) {signal}")
                if not in_portfolio:
                    output["🆕 Рекомендации (монеты вне портфеля)"].append(f"{symbol}: растёт — ✅ *Рассмотреть к покупке*")
            elif change <= -2:
                signal = "🔴 *Продавать*"
                output["📉 Падающие монеты"].append(f"{symbol}: ${price:.2f} ({change:+.2f}%) {signal}")
                if not in_portfolio:
                    output["🆕 Рекомендации (монеты вне портфеля)"].append(f"{symbol}: падает — ❌ *Избегать покупки*")
            else:
                signal = "🟡 Держать"
                output["⏸️ Стабильные монеты"].append(f"{symbol}: ${price:.2f} ({change:+.2f}%) {signal}")
                if not in_portfolio:
                    output["🆕 Рекомендации (монеты вне портфеля)"].append(f"{symbol}: стабилен — ⚠️ *Под наблюдением*")

        # Формируем финальный текст
        lines = []
        for section, coins in output.items():
            if coins:
                lines.append(f"*{section}*:")
                lines.extend([f"- {c}" for c in coins])
                lines.append("")

        return "\n".join(lines).strip()

    except Exception as e:
        return f"Ошибка при анализе рынка: {e}"
