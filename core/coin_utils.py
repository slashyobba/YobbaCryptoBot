import requests
from datetime import datetime, timedelta

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

def load_symbol_id_map():
    """Получает полный список монет и строит словарь symbol → id."""
    resp = requests.get(f"{COINGECKO_BASE}/coins/list")
    resp.raise_for_status()
    data = resp.json()
    # Возможны коллизии, поэтому сохраняем список ids per symbol
    symbol_map = {}
    for coin in data:
        sym = coin['symbol'].lower()
        symbol_map.setdefault(sym, []).append(coin['id'])
    return symbol_map

_symbol_map_cache = None

def get_coingecko_id(symbol: str):
    global _symbol_map_cache
    if _symbol_map_cache is None:
        _symbol_map_cache = load_symbol_id_map()
    ids = _symbol_map_cache.get(symbol.lower())
    if not ids:
        return None
    # Если несколько совпадений — выбираем первое (можно доработать выбор)
    return ids[0]

def is_new_coin_by_genesis(genesis_date_str, threshold_days=90):
    if not genesis_date_str:
        return False
    try:
        dt = datetime.strptime(genesis_date_str, "%Y-%m-%d")
        return datetime.now() - dt < timedelta(days=threshold_days)
    except:
        return False
