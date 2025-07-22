import pandas as pd


def detect_origine(row):
    if row["type"] == "reward":
        return "staking"
    elif row["type"] == "deposit":
        return "dépôt"
    elif row["type"] == "transfer":
        return "transfert"
    elif row["type"] == "trade":
        return "achat/vente"
    elif row["type"] == "spend":
        return "paiement"
    elif row["type"] == "receive":
        if row["subtype"] == "airdrop":
            return "airdrop"
        return "réception"
    else:
        return "autre"


def ajouter_colonne_origine(df_clean):
    df = df_clean.copy()
    df["origine"] = df.apply(detect_origine, axis=1)
    return df


def calcul_total_investi(df_with_origine, eur_assets=None):
    if eur_assets is None:
        eur_assets = ["EUR", "EUR.HOLD", "ZEUR"]

    # On considère comme investissement tout envoi de fonds depuis ton portefeuille
    df_invest = df_with_origine[
        (df_with_origine["type"].isin(["trade", "transfer", "spend"]))
        & (~df_with_origine["asset"].isin(eur_assets))
        & (df_with_origine["amount"] < 0)
    ].copy()

    df_invest["investi (€)"] = df_invest.apply(
        lambda row: abs(row["amount"]) * row.get("prix_eur", 0), axis=1
    )

    total_par_crypto = df_invest.groupby("asset")["investi (€)"].sum()
    return total_par_crypto.reset_index().rename(
        columns={"asset": "Crypto", "investi (€)": "Total investi (€)"}
    )
