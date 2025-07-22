import requests
import time

_CACHE = {}
_CACHE_TIME = 3600  # 1h
_LAST_FETCH = 0


def _refresh_cache():
    global _CACHE, _LAST_FETCH
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "eur",
            "order": "market_cap_desc",
            "per_page": 500,
            "page": 1,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        _CACHE = {
            coin["symbol"].upper(): coin["id"]
            for coin in data
            if "symbol" in coin and "id" in coin
        }
        _LAST_FETCH = time.time()
        print(
            f"[🧠 Cache CoinGecko chargé : {_CACHE.get('BTC')} {len(_CACHE)} entrées]"
        )
    except Exception as e:
        print(f"⚠️ Erreur lors du rafraîchissement CoinGecko: {e}")


def get_coingecko_id(symbol):
    if time.time() - _LAST_FETCH > _CACHE_TIME or not _CACHE:
        _refresh_cache()
    id = _CACHE.get(symbol.upper())
    print(f"[get_coingecko_id] {symbol.upper()} → {id}")
    return id
