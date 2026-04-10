import requests


# ---------- SAFE FLOAT ----------
def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


# ---------- CRYPTO PRICES ----------
def get_crypto_prices():
    """
    Fetch 20 crypto prices safely from CoinGecko
    """

    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": ",".join([
            "bitcoin",
            "ethereum",
            "solana",
            "cardano",
            "ripple",
            "dogecoin",
            "polkadot",
            "litecoin",
            "tron",
            "avalanche-2",
            "chainlink",
            "polygon",
            "stellar",
            "cosmos",
            "monero",
            "ethereum-classic",
            "near",
            "aptos",
            "arbitrum",
            "optimism"
        ]),
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {}

        data = response.json()

        prices = {
            "Bitcoin": safe_float(data.get("bitcoin", {}).get("usd")),
            "Ethereum": safe_float(data.get("ethereum", {}).get("usd")),
            "Solana": safe_float(data.get("solana", {}).get("usd")),
            "Cardano": safe_float(data.get("cardano", {}).get("usd")),
            "XRP": safe_float(data.get("ripple", {}).get("usd")),
            "Dogecoin": safe_float(data.get("dogecoin", {}).get("usd")),
            "Polkadot": safe_float(data.get("polkadot", {}).get("usd")),
            "Litecoin": safe_float(data.get("litecoin", {}).get("usd")),
            "Tron": safe_float(data.get("tron", {}).get("usd")),
            "Avalanche": safe_float(data.get("avalanche-2", {}).get("usd")),
            "Chainlink": safe_float(data.get("chainlink", {}).get("usd")),
            "Polygon": safe_float(data.get("polygon", {}).get("usd")),
            "Stellar": safe_float(data.get("stellar", {}).get("usd")),
            "Cosmos": safe_float(data.get("cosmos", {}).get("usd")),
            "Monero": safe_float(data.get("monero", {}).get("usd")),
            "Ethereum Classic": safe_float(data.get("ethereum-classic", {}).get("usd")),
            "NEAR": safe_float(data.get("near", {}).get("usd")),
            "Aptos": safe_float(data.get("aptos", {}).get("usd")),
            "Arbitrum": safe_float(data.get("arbitrum", {}).get("usd")),
            "Optimism": safe_float(data.get("optimism", {}).get("usd")),
        }

        return prices

    except Exception as e:
        print("Error fetching crypto data:", e)
        return {}


# ---------- FOREX ----------
def get_forex_price():
    """
    Fetch EUR/USD exchange rate safely
    """

    url = "https://api.exchangerate.host/latest?base=EUR&symbols=USD"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return 0.0

        data = response.json()

        return safe_float(data.get("rates", {}).get("USD"))

    except Exception as e:
        print("Error fetching forex data:", e)
        return 0.0