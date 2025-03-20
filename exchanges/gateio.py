import requests
from datetime import datetime, timezone, timedelta
from gate_api import ApiClient, Configuration, FuturesApi
from gate_api.exceptions import GateApiException

KYIV_TZ = timezone(timedelta(hours=2))

def setup_gate_client(api_key, api_secret):
    config = Configuration(
        key=api_key,
        secret=api_secret,
        host="https://api.gateio.ws/api/v4"
    )
    return ApiClient(config)

def get_gate_data(symbol="BTC_USDT", api_key="", api_secret=""):
    try:
        if not api_key or not api_secret:
            print(f"Gate.io для {symbol}: API ключі не надані, пропускаємо.")
            return None

        # Ініціалізація клієнта
        client = setup_gate_client(api_key, api_secret)
        api_instance = FuturesApi(client)

        # Запит фандінг-рейтів
        funding_rates = api_instance.list_futures_funding_rate_history(settle="usdt", contract=symbol)
        last_funding = funding_rates[-1]

        funding_rate = float(last_funding._r) * 100
        next_funding_time = "?"

        # Запит mark price через правильний endpoint
        ticker_url = f"https://api.gateio.ws/api/v4/futures/usdt/tickers?contract={symbol}"
        ticker_response = requests.get(ticker_url)
        ticker_response.raise_for_status()
        ticker_data = ticker_response.json()[0]
        mark_price = float(ticker_data["index_price"])

        print(f"{symbol} (Gate.io) — Наступний фандінг: {next_funding_time}")
        print(f"  - Фандінг-рейт: {funding_rate:.4f}%")
        print(f"  - Mark Price: {mark_price:.2f} USD")
        print(f"  - Funding Rate Prediction: Немає даних")
        print(f"  * Точний час фандінгу недоступний через API, перевірте на Gate.io\n")

        return {
            "Exchange": "Gate.io",
            "Symbol": symbol,
            "Next Funding (%)": funding_rate,
            "Mark Price (USD)": mark_price,
            "Funding Prediction (%)": None,
            "Next Funding Time": next_funding_time
        }

    except GateApiException as e:
        print(f"Помилка API Gate.io для {symbol}: {e}")
        return None
    except Exception as e:
        print(f"Помилка при отриманні даних з Gate.io для {symbol}: {e}")
        if 'ticker_response' in locals():
            print(f"Response text: {ticker_response.text}")
        return None