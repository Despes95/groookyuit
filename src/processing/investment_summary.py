import pandas as pd
from src.api.api_kraken import fetch_kraken_balance
from src.utils.normalize import normalize_asset


def compute_staking_value(staked_info):
    return sum(
        float(info["amount"]) * info["price_eur"] for info in staked_info.values()
    )


def build_crypto_summary(df_clean, staked_info, current_prices, kraken_balance):
    eur_assets = ["EUR", "EUR.HOLD", "ZEUR"]

    crypto_summary = (
        df_clean[~df_clean["asset"].isin(eur_assets)].groupby("asset")["amount"].sum()
    )
    crypto_summary = crypto_summary[abs(crypto_summary) > 1e-10]

    for asset, info in staked_info.items():
        crypto_summary[asset] = float(info["amount"])

    if kraken_balance:
        for asset, value in kraken_balance.items():
            if float(value) > 1e-10:
                crypto_summary[asset] = float(value)

    return crypto_summary


def summarize_crypto(crypto_summary, average_prices, staked_info, current_prices):
    crypto_values = {}
    for asset, amount in crypto_summary.items():
        norm = normalize_asset(asset)
        base_asset = norm
        current_price = staked_info.get(asset, {}).get(
            "price_eur", current_prices.get(base_asset, 0)
        )
        value = amount * current_price
        avg_price = average_prices.get(asset, 0)
        performance = (
            ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
        )
        crypto_values[asset] = {
            "amount": amount,
            "value_eur": round(value, 4),
            "current_price_eur": current_price,
            "avg_purchase_price_eur": avg_price,
            "performance_pct": round(performance, 2),
            "unlock_date": staked_info.get(asset, {}).get("unlock_date", ""),
            "yield": staked_info.get(asset, {}).get("yield", ""),
            "emoji": (
                "🔒"
                if asset in staked_info
                else (
                    "📈"
                    if asset in ["USDG", "USDC"]
                    else "🚀" if performance > 0 else ""
                )
            ),
        }
    return (
        pd.DataFrame.from_dict(crypto_values, orient="index")
        .reset_index()
        .rename(
            columns={
                "index": "Actif",
                "amount": "Montant",
                "value_eur": "Valeur (€)",
                "current_price_eur": "Prix actuel (€)",
                "avg_purchase_price_eur": "Prix d’achat moyen (€)",
                "performance_pct": "Performance (%)",
                "unlock_date": "Date de déverrouillage",
                "yield": "Rendement",
                "emoji": "Emoji",
            }
        )
    )


def summarize_staked_info():
    return {
        "DOT28.S": {
            "amount": 5.6354189750,
            "unlock_date": "2025-07-17",
            "yield": "9-15%",
        },
        "INJ.B": {
            "amount": 1.0156119506,
            "unlock_date": "2025-07-17",
            "yield": "7-12%",
        },
        "SUI.B": {"amount": 16.01225, "unlock_date": "2025-07-17", "yield": "1-3%"},
        "DOT.F": {"amount": 3.2903966721, "unlock_date": "", "yield": "5-9%"},
        "ETH.F": {"amount": 0.0082980884, "unlock_date": "", "yield": "1-3%"},
        "SOL.F": {"amount": 0.0000012200, "unlock_date": "", "yield": "3-6%"},
        "XBT.F": {"amount": 0.0004325962, "unlock_date": "", "yield": "0.1%"},
        "INJ.F": {"amount": 0.0000038289, "unlock_date": "", "yield": "3-6%"},
        "SUI.F": {"amount": 0.00076, "unlock_date": "", "yield": "1-2%"},
    }
