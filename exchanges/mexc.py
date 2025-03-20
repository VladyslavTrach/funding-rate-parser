import requests
from datetime import datetime, timezone, timedelta

KYIV_TZ = timezone(timedelta(hours=2))

def get_mexc_data(symbol="BTC_USDT"):
    try:
        funding_url = f"https://futures.mexc.com/api/v1/contract/funding_rate/{symbol}"
        funding_response = requests.get(funding_url)
        funding_response.raise_for_status()
        funding_data = funding_response.json()["data"]

        funding_rate = float(funding_data["fundingRate"]) * 100
        next_funding_time = "?"

        ticker_url = f"https://futures.mexc.com/api/v1/contract/index_price/{symbol}"
        ticker_response = requests.get(ticker_url)
        ticker_response.raise_for_status()
        ticker_data = ticker_response.json()["data"]

        mark_price = float(ticker_data["indexPrice"])

        print(f"{symbol} (MEXC) — Оновлено: {next_funding_time}")
        print(f"  - Наступний фандінг-рейт: {funding_rate:.4f}%")
        print(f"  - Mark Price: {mark_price:.2f} USD")
        print(f"  - Funding Rate Prediction: Немає даних\n")

        return {
            "Exchange": "MEXC",
            "Symbol": symbol,
            "Next Funding (%)": funding_rate,
            "Mark Price (USD)": mark_price,
            "Funding Prediction (%)": None,
            "Next Funding Time": next_funding_time
        }
    except Exception as e:
        print(f"Помилка при отриманні даних з MEXC для {symbol}: {e}")
        return None