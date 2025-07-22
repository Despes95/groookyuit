import streamlit as st
import pandas as pd
from src.processing.parse_transactions import analyser_ledger
from src.processing.investment_summary import (
    summarize_staked_info,
    compute_staking_value,
    build_crypto_summary,
    summarize_crypto,
)
from src.processing.origine import ajouter_colonne_origine, calcul_total_investi
from src.utils.mapping import get_display_name, update_mapping_if_new_assets
from src.utils.pricing import get_price
from src.utils.normalize import normalize_asset
from src.api.api_coingecko import fetch_multiple_prices_coingecko

st.set_page_config(page_title="Kraken Crypto Tracker", layout="wide", page_icon="💰")
st.title("📊 Kraken Crypto Tracker")

with st.spinner("Chargement des données..."):
    today = pd.to_datetime("today")
    period_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = (period_start + pd.offsets.MonthEnd(0)).replace(
        hour=23, minute=59, second=59
    )

    ledger_data = analyser_ledger(period_start, period_end)
    if not ledger_data:
        st.error("Aucune donnée disponible depuis l'API Kraken.")
    else:
        df_clean = ledger_data["df_clean"]
        average_prices = ledger_data["average_prices"]
        current_prices = ledger_data["current_prices"]
        kraken_balance = ledger_data["kraken_balance"]

        fallback_prices = fetch_multiple_prices_coingecko(
            [
                "bitcoin",
                "ethereum",
                "dogecoin",
                "xrp",
                "polkadot",
                "injective-protocol",
                "sui",
                "hedera",
                "floki",
                "pepe",
                "solana",
            ]
        )
        st.write("🧪 fallback_prices", fallback_prices)

        staked_info = summarize_staked_info()
        for asset in staked_info:
            if isinstance(asset, str) and asset.strip():
                prix = get_price(asset, current_prices, fallback_prices)
            else:
                prix = 0.0
            staked_info[asset]["price_eur"] = prix

        df_with_origine = ajouter_colonne_origine(df_clean)
        df_with_origine["asset"] = df_with_origine["asset"].apply(normalize_asset)
        df_with_origine["prix_eur"] = df_with_origine.apply(
            lambda row: get_price(row["asset"], current_prices, fallback_prices), axis=1
        )
        st.write(
            "🧪 DOGE dans df_with_origine",
            df_with_origine[df_with_origine["asset"] == "DOGE"],
        )
        total_investi = calcul_total_investi(df_with_origine)

        staking_value = compute_staking_value(staked_info)
        crypto_summary = build_crypto_summary(
            df_clean, staked_info, current_prices, kraken_balance
        )
        crypto_df = summarize_crypto(
            crypto_summary, average_prices, staked_info, current_prices
        )

        crypto_df["Actif"] = crypto_df["Actif"].apply(normalize_asset)
        crypto_df = crypto_df.groupby("Actif", as_index=False).agg(
            {
                "Montant": "sum",
                "Valeur (€)": "sum",
                "Prix actuel (€)": "mean",
                "Prix d’achat moyen (€)": "mean",
                "Performance (%)": "mean",
                "Date de déverrouillage": lambda x: ", ".join(
                    set(x.dropna().astype(str))
                ),
                "Rendement": lambda x: ", ".join(set(x.dropna().astype(str))),
                "Emoji": lambda x: (
                    "🔒"
                    if any(e == "🔒" for e in x)
                    else "🚀" if any(e == "🚀" for e in x) else ""
                ),
            }
        )
        crypto_df["Staké"] = crypto_df["Emoji"].apply(
            lambda e: "Oui" if "🔒" in e else "Non"
        )

        st.subheader("💼 Portefeuille crypto")

        crypto_df["Actif"] = crypto_df["Actif"].apply(get_display_name)
        new_assets = update_mapping_if_new_assets(crypto_df["Actif"].tolist())
        if new_assets:
            st.warning(f"⚠️ Actifs non mappés détectés : {', '.join(new_assets)}")

        st.dataframe(crypto_df, use_container_width=True)

        btc_check = crypto_df[crypto_df["Actif"].str.contains("Bitcoin")]
        st.write("🧪 DEBUG Bitcoin", btc_check)

        total_portfolio_value = crypto_df["Valeur (€)"].sum()
        st.metric("💰 Valeur totale du portefeuille", f"{total_portfolio_value:,.2f} €")
        st.metric("🔒 Valeur en staking estimée", f"{staking_value:,.2f} €")

        st.subheader("💶 Total investi par crypto")
        total_investi["Crypto"] = (
            total_investi["Crypto"].apply(normalize_asset).apply(get_display_name)
        )
        st.dataframe(total_investi, use_container_width=True)

        with st.expander("📜 Historique des transactions (nettoyé)", expanded=False):
            st.dataframe(df_with_origine, use_container_width=True)
