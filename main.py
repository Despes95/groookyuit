import pandas as pd
from src.processing.parse_transactions import analyser_ledger
from src.processing.investment_summary import (
    summarize_staked_info,
    compute_staking_value,
    build_crypto_summary,
    summarize_crypto,
)


def main():
    today = pd.to_datetime("today")
    period_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = (period_start + pd.offsets.MonthEnd(0)).replace(
        hour=23, minute=59, second=59
    )

    ledger_data = analyser_ledger(period_start, period_end)
    if not ledger_data:
        print("Aucune donnée disponible.")
        return

    df_clean = ledger_data["df_clean"]
    average_prices = ledger_data["average_prices"]
    current_prices = ledger_data["current_prices"]
    kraken_balance = ledger_data["kraken_balance"]

    staked_info = summarize_staked_info()
    for asset in staked_info:
        base = asset.split(".")[0] if "." in asset else asset
        staked_info[asset]["price_eur"] = current_prices.get(base, 0)

    staking_value = compute_staking_value(staked_info)
    crypto_summary = build_crypto_summary(
        df_clean, staked_info, current_prices, kraken_balance
    )
    crypto_df = summarize_crypto(
        crypto_summary, average_prices, staked_info, current_prices
    )

    print("\nRésumé portefeuille :")
    print(crypto_df.to_string(index=False))
    print(f"\nValeur en staking estimée : {staking_value:.2f} EUR")


if __name__ == "__main__":
    main()
