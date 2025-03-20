import requests
from datetime import datetime, timezone, timedelta

KYIV_TZ = timezone(timedelta(hours=2))

def get_bybit_data(symbol="BTCUSDT"):
    try:
        funding_url = f"https://api.bybit.com/v5/market/funding/history?category=linear&symbol={symbol}"
        funding_response = requests.get(funding_url)
        funding_response.raise_for_status()
        funding_data = funding_response.json()["result"]["list"][0]

        funding_rate = float(funding_data["fundingRate"]) * 100
        last_funding_time = int(funding_data["fundingRateTimestamp"]) // 1000
        next_funding_time_utc = datetime.fromtimestamp(last_funding_time, tz=timezone.utc) + timedelta(hours=8)
        next_funding_time_kyiv = next_funding_time_utc.astimezone(KYIV_TZ).strftime('%Y-%m-%d %H:%M:%S')

        ticker_url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
        ticker_response = requests.get(ticker_url)
        ticker_response.raise_for_status()
        ticker_data = ticker_response.json()["result"]["list"][0]

        mark_price = float(ticker_data["markPrice"])

        print(f"{symbol} (Bybit) — Наступний фандінг: {next_funding_time_kyiv}")
        print(f"  - Фандінг-рейт: {funding_rate:.4f}%")
        print(f"  - Mark Price: {mark_price:.2f} USD")
        print(f"  - Funding Rate Prediction: Немає даних\n")

        return {
            "Exchange": "Bybit",
            "Symbol": symbol,
            "Next Funding (%)": funding_rate,
            "Mark Price (USD)": mark_price,
            "Funding Prediction (%)": None,
            "Next Funding Time": next_funding_time_kyiv
        }
    except Exception as e:
        print(f"Помилка при отриманні даних з Bybit для {symbol}: {e}")
        return None