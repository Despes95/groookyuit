# Mapping des noms de crypto pour affichage lisible
DISPLAY_NAMES = {
    "HBAR": "Hedera",
    "SUI": "Sui",
    "XRP": "XRP",
    "XBT": "Bitcoin",
    "BTC": "Bitcoin",
    "DOGE": "Dogecoin",
    "DOT": "Polkadot",
    "ETH": "Ethereum",
    "INJ": "Injective",
    "PEPE": "Pepe",
    "SOL": "Solana",
    "FLOKI": "Floki",
    # Ajoute d'autres actifs ici si besoin
}


def get_display_name(asset):
    base = asset.split(".")[0] if "." in asset else asset
    is_staked = any(s in asset for s in [".S", ".B", ".F"])
    label = DISPLAY_NAMES.get(base, base)
    return f"{label} (staké)" if is_staked else label


def update_mapping_if_new_assets(asset_list):
    unknown = []
    for asset in asset_list:
        base = asset.split(".")[0] if "." in asset else asset
        if base not in DISPLAY_NAMES:
            unknown.append(base)
    return unknown  # à logger ou notifier
