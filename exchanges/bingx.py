import requests
from datetime import datetime, timezone, timedelta

KYIV_TZ = timezone(timedelta(hours=2))

def get_bingx_data(symbol="BTC-USDT"):
    try:
        funding_url = f"https://open-api.bingx.com/openApi/swap/v2/quote/premiumIndex?symbol={symbol}"
        funding_response = requests.get(funding_url, timeout=10)
        funding_response.raise_for_status()
        funding_data = funding_response.json()

        if funding_data["code"] != 0 or not funding_data.get("data"):
            raise ValueError(f"API повернуло помилку: {funding_data.get('msg', 'Немає даних')}")

        funding_info = funding_data["data"]  # data — це словник, а не список
        funding_rate = float(funding_info["lastFundingRate"]) * 100
        next_funding_time_utc = datetime.fromtimestamp(int(funding_info["nextFundingTime"]) // 1000, tz=timezone.utc)
        next_funding_time_kyiv = next_funding_time_utc.astimezone(KYIV_TZ).strftime('%Y-%m-%d %H:%M:%S')
        mark_price = float(funding_info["markPrice"])

        print(f"{symbol} (BingX) — Наступний фандінг: {next_funding_time_kyiv}")
        print(f"  - Фандінг-рейт: {funding_rate:.4f}%")
        print(f"  - Mark Price: {mark_price:.2f} USD")
        print(f"  - Funding Rate Prediction: Немає даних\n")

        return {
            "Exchange": "BingX",
            "Symbol": symbol,
            "Next Funding (%)": funding_rate,
            "Mark Price (USD)": mark_price,
            "Funding Prediction (%)": None,
            "Next Funding Time": next_funding_time_kyiv
        }
    except Exception as e:
        print(f"Помилка при отриманні даних з BingX для {symbol}: {e}")
        return None

# Тест
if __name__ == "__main__":
    result = get_bingx_data("BTC-USDT")
    print(result)