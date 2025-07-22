# Nettoyage et parsing des transactions Kraken
import pandas as pd
from src.api.api_kraken import (
    fetch_kraken_balance,
    fetch_kraken_ticker,
    fetch_kraken_transactions,
)
from src.api.api_coingecko import fetch_multiple_prices_coingecko


def analyser_ledger(period_start=None, period_end=None):
    # Récupération des prix via Kraken ou CoinGecko en fallback
    current_prices = fetch_kraken_ticker()
    if not current_prices:
        current_prices = fetch_multiple_prices_coingecko(
            [
                "dot",
                "inj",
                "sui",
                "usdc",
                "hbar",
                "sol",
                "bitcoin",
                "dogecoin",
                "ripple",
                "ethereum",
                "pepe",
                "floki",
            ]
        )

    # Transactions Kraken
    df = fetch_kraken_transactions(period_start, period_end)
    if df is None or df.empty:
        return None

    # Nettoyage / enrichissement
    df["month"] = df["time"].dt.to_period("M")
    df_clean = df[
        ["time", "month", "type", "subtype", "asset", "wallet", "amount", "fee"]
    ].copy()

    # Dépôts crypto uniquement
    eur_assets = ["EUR", "EUR.HOLD", "ZEUR"]
    df_deposit = df_clean[
        (df_clean["type"].isin(["deposit", "receive"]))
        & (~df_clean["asset"].isin(eur_assets))
    ].copy()

    # Prix moyens d’achat
    average_prices = (
        df_deposit.groupby("asset").apply(
            lambda x: (
                (
                    (
                        x["amount"]
                        * current_prices.get(
                            (
                                x["asset"].iloc[0].split(".")[0]
                                if "." in x["asset"].iloc[0]
                                else x["asset"].iloc[0]
                            ),
                            0,
                        )
                    ).sum()
                    / x["amount"].sum()
                )
                if x["amount"].sum() != 0
                else 0
            )
        )
        if not df_deposit.empty
        else pd.Series({}, dtype=float)
    )

    # Solde Kraken
    kraken_balance = fetch_kraken_balance()

    # Données prêtes pour la suite (résumé, staking, ROI)
    return {
        "df_clean": df_clean,
        "average_prices": average_prices,
        "current_prices": current_prices,
        "kraken_balance": kraken_balance,
    }
