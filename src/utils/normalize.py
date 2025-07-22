# Normalisation des noms Kraken vers des standards clairs (BTC, ETH, etc.)

NORMALIZED = {
    "XXBT": "BTC",
    "XBT": "BTC",
    "XETH": "ETH",
    "ETH2.S": "ETH",
    "XDG": "DOGE",
    "XXDG": "DOGE",
    "XXRP": "XRP",
    "ZEUR": "EUR",
    "USDT": "USDT",
    "USDC": "USDC",
    "USDG": "USDC",
    "XDOT": "DOT",
    # ajoute ici d'autres variations Kraken si besoin
}


def normalize_asset(asset):
    base = asset.split(".")[0] if "." in asset else asset
    return NORMALIZED.get(base, base)
