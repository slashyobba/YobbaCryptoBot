import os
import requests

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_SECRET")

def get_headers():
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": "",
        "ACCESS-TIMESTAMP": "",
        "ACCESS-PASSPHRASE": "",
        "Content-Type": "application/json"
    }

async def get_portfolio_value():
    # Заглушка — реальное подключение на следующем этапе
    return "*Текущий портфель:*\n- ETH: $95.26\n- BTC: $30.21\n- и т.д."
