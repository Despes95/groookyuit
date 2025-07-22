from src.utils.normalize import normalize_asset
from src.api.coingecko_util import get_coingecko_id
import requests

price_memory_cache = {}


def get_base_asset(asset):
    return asset.split(".")[0] if "." in asset else asset


def get_price(asset, current_prices, fallback_prices=None):
    base = normalize_asset(get_base_asset(asset))

    if base in price_memory_cache:
        print(f"[🧠 Cache mémoire] {base} → {price_memory_cache[base]}")
        return price_memory_cache[base]

    price_kraken = current_prices.get(base)
    if price_kraken and price_kraken > 0:
        return price_kraken

    if fallback_prices:
        fallback = fallback_prices.get(base.upper()) or fallback_prices.get(
            base.lower()
        )
        if fallback and fallback > 0:
            print(f"[CoinGecko fallback] {base.upper()} → {fallback}")
            price_memory_cache[base] = fallback
            return fallback

    # Appel dynamique CoinGecko
    cg_id = get_coingecko_id(base)
    print(f"[Dynamique CG] {base} → {cg_id}")
    if cg_id:
        try:
            print(f"[🔍 API call] CoinGecko {cg_id} ...")
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=eur"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            print(f"[🧾 Raw CoinGecko data pour {cg_id}] {data}")

            for key, val in data.items():
                if isinstance(val, dict) and "eur" in val:
                    prix = float(val["eur"])
                    print(f"[✅ CoinGecko fallback loop] {key} → {prix}")
                    price_memory_cache[base] = prix
                    return prix

        except Exception as e:
            print(f"[❌ Erreur CoinGecko] {cg_id} : {e}")

    print(f"❌ Prix introuvable pour {asset} → {base}")
    return 0.0
