# data_fetcher.py
import pandas as pd
from exchanges.binance import get_binance_data
from exchanges.gateio import get_gate_data
from exchanges.mexc import get_mexc_data
from exchanges.bybit import get_bybit_data
from exchanges.bingx import get_bingx_data
from config import GATE_API_KEY, GATE_API_SECRET, BASE_SYMBOLS, EXCHANGE_FORMATS, EXCHANGES

def fetch_funding_data():
    """Збір даних про фандінг-рейти з усіх бірж."""
    data = []
    for exchange in EXCHANGES:
        symbols = [EXCHANGE_FORMATS[exchange](symbol) for symbol in BASE_SYMBOLS]
        for symbol in symbols:
            if exchange == "Binance":
                result = get_binance_data(symbol)
            elif exchange == "Gate.io":
                result = get_gate_data(symbol, GATE_API_KEY, GATE_API_SECRET)
            elif exchange == "MEXC":
                result = get_mexc_data(symbol)
            elif exchange == "Bybit":
                result = get_bybit_data(symbol)
            elif exchange == "BingX":
                result = get_bingx_data(symbol)
            if result:
                data.append(result)
    return pd.DataFrame(data) if data else None

def calculate_funding_spread(df):
    """Обчислення спреду фандінг-рейтів між біржами для кожного символу."""
    if df is None or df.empty:
        return None
    
    spread_data = []
    for base_symbol in BASE_SYMBOLS:
        # Фільтруємо рядки DataFrame, де Symbol містить base_symbol
        symbol_data = df[df["Symbol"].str.contains(base_symbol, case=True)]
        if symbol_data.empty or len(symbol_data) < 2:
            continue  # Потрібно принаймні 2 біржі для порівняння

        # Отримуємо фандінг-рейти для цього символу
        funding_rates = symbol_data.set_index("Exchange")["Next Funding (%)"]
        max_rate = funding_rates.max()
        min_rate = funding_rates.min()
        spread = max_rate - min_rate
        max_exchange = funding_rates.idxmax()
        min_exchange = funding_rates.idxmin()

        spread_data.append({
            "Symbol": base_symbol,
            "Max Funding (%)": max_rate,
            "Max Exchange": max_exchange,
            "Min Funding (%)": min_rate,
            "Min Exchange": min_exchange,
            "Spread (%)": spread
        })

    return pd.DataFrame(spread_data) if spread_data else None