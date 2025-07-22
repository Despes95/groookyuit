# Appels Kraken (balance, transactions, prix)
import time
import hashlib
import hmac
import base64
import requests
from decouple import config
import pandas as pd

def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def fetch_kraken_ticker():
    log_message("Début de fetch_kraken_ticker")
    url = "https://api.kraken.com/0/public/Ticker"
    pairs = [
        "DOTEUR", "INJEUR", "SUIEUR", "USDCEUR", "HBAREUR",
        "SOLEUR", "XBTEUR", "DOGEEUR", "XRPEUR", "ETHEUR",
        "PEPEEUR", "FLOKIEUR",
    ]
    params = {"pair": ",".join(pairs)}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("error"):
            log_message(f"Erreur API Kraken Ticker : {data['error']}")
            return {}
        prices = {
            pair.replace("EUR", "").replace("Z", ""): float(info["c"][0])
            for pair, info in data.get("result", {}).items()
        }
        prices["USDG"] = prices.get("USDC", 0.8587)
        log_message(f"Prix récupérés : {prices}")
        return prices
    except requests.RequestException as e:
        log_message(f"Erreur réseau dans fetch_kraken_ticker : {e}")
        return {}

def fetch_kraken_balance():
    log_message("Début de fetch_kraken_balance")
    api_key = config("KRAKEN_API_KEY", default=None)
    api_secret = config("KRAKEN_API_SECRET", default=None)
    if not api_key or not api_secret:
        log_message("Erreur : Clés API manquantes ou invalides dans .env")
        return None

    url = "https://api.kraken.com/0/private/Balance"
    max_retries = 3
    retries = 0

    while retries < max_retries:
        api_nonce = str(int(time.time() * 1000000))
        api_post = f"nonce={api_nonce}"
        message = api_nonce + api_post
        sha256 = hashlib.sha256(message.encode()).digest()
        signature = hmac.new(
            base64.b64decode(api_secret),
            ("/0/private/Balance".encode() + sha256),
            hashlib.sha512,
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()

        headers = {
            "API-Key": api_key,
            "API-Sign": signature_b64,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(url, data=api_post, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("error"):
                log_message(f"Erreur API Kraken : {data['error']}")
                return None
            log_message("Solde Kraken récupéré avec succès")
            log_message(f"Soldes bruts : {data.get('result', {})}")
            staked_assets = {
                k: v
                for k, v in data.get("result", {}).items()
                if ".S" in k or ".F" in k or ".B" in k
            }
            log_message(f"Actifs en staking : {staked_assets}")
            return data.get("result", {})
        except requests.RequestException as e:
            log_message(f"Erreur réseau (tentative {retries + 1}/{max_retries}) : {e}")
            retries += 1
            time.sleep(2**retries)
    log_message("Échec de fetch_kraken_balance après 3 tentatives")
    return None

def fetch_kraken_transactions(period_start=None, period_end=None):
    log_message("Début de fetch_kraken_transactions")
    api_key = config("KRAKEN_API_KEY", default=None)
    api_secret = config("KRAKEN_API_SECRET", default=None)
    if not api_key or not api_secret:
        log_message("Erreur : Clés API manquantes ou invalides dans .env")
        return None

    url = "https://api.kraken.com/0/private/Ledgers"
    max_retries = 3
    retries = 0

    while retries < max_retries:
        api_nonce = str(int(time.time() * 1000000))
        api_post = f"nonce={api_nonce}"
        if period_start:
            api_post += f"&start={int(period_start.timestamp())}"
        if period_end:
            api_post += f"&end={int(period_end.timestamp())}"

        message = api_nonce + api_post
        sha256 = hashlib.sha256(message.encode()).digest()
        signature = hmac.new(
            base64.b64decode(api_secret),
            ("/0/private/Ledgers".encode() + sha256),
            hashlib.sha512,
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()

        headers = {
            "API-Key": api_key,
            "API-Sign": signature_b64,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(url, data=api_post, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("error"):
                log_message(f"Erreur API Kraken : {data['error']}")
                return None

            transactions = []
            for ledger_id, info in data.get("result", {}).get("ledger", {}).items():
                transactions.append(
                    {
                        "txid": ledger_id,
                        "time": pd.to_datetime(float(info.get("time", 0)), unit="s"),
                        "type": info.get("type", ""),
                        "subtype": info.get("subtype", ""),
                        "asset": info.get("asset", ""),
                        "wallet": info.get("aclass", "spot"),
                        "amount": float(info.get("amount", 0)),
                        "fee": float(info.get("fee", 0)),
                    }
                )
            df = pd.DataFrame(transactions)
            log_message(f"{len(df)} transactions récupérées via API")
            log_message(f"Colonnes du DataFrame : {list(df.columns)}")
            log_message(f"Premières lignes :\n{df.head().to_string()}")
            return df
        except requests.RequestException as e:
            log_message(f"Erreur réseau (tentative {retries + 1}/{max_retries}) : {e}")
            retries += 1
            time.sleep(2**retries)
    log_message("Échec de fetch_kraken_transactions après 3 tentatives")
    return None
