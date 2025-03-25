# exchanges/gate.py
import gate_api
from gate_api.exceptions import GateApiException
from config import GATE_API_KEY, GATE_API_SECRET
from datetime import datetime
import logging

def get_gate_data(symbol):
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4",
        key=GATE_API_KEY,
        secret=GATE_API_SECRET
    )
    api_client = gate_api.ApiClient(configuration)
    futures_api = gate_api.FuturesApi(api_client)

    try:
        # Отримання фандінг-рейтів
        funding_rates = futures_api.list_futures_funding_rate_history(settle='usdt', contract=symbol, limit=1)
        logging.info(f"Gate.io funding rate response for {symbol}: {funding_rates}")
        
        if not funding_rates:
            logging.error(f"No funding rate data for {symbol}")
            return None
        
        # Отримання маркової ціни
        tickers = futures_api.list_futures_tickers(settle='usdt', contract=symbol)
        logging.info(f"Gate.io tickers response for {symbol}: {tickers}")
        
        if not tickers:
            logging.error(f"No ticker data for {symbol}")
            return None
        
        latest_funding = funding_rates[0]
        latest_ticker = tickers[0]
        
        funding_rate = float(latest_funding.r) * 100
        mark_price = float(latest_ticker.mark_price)
        next_funding_time = datetime.fromtimestamp(int(latest_funding.t)).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            "Exchange": "Gate.io",
            "Symbol": symbol,
            "Next Funding (%)": funding_rate,
            "Mark Price (USD)": mark_price,
            "Funding Prediction (%)": None,
            "Next Funding Time": next_funding_time
        }
    except GateApiException as e:
        logging.error(f"Gate.io API error for {symbol}: {e}")
        return None