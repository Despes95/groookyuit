import requests
from src.api.coingecko_util import get_coingecko_id

def fetch_multiple_prices_coingecko(symbols):
    ids = []
    symbol_to_id = {}
    for sym in symbols:
        cg_id = get_coingecko_id(sym)
        if cg_id:
            ids.append(cg_id)
            symbol_to_id[sym.upper()] = cg_id

    if not ids:
        return {}

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=eur"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            sym: data[cg_id]["eur"]
            for sym, cg_id in symbol_to_id.items()
            if cg_id in data and "eur" in data[cg_id]
        }
    except requests.RequestException:
        return {}