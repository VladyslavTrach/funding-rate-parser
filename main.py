import pandas as pd
import requests
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from exchanges.mexc import get_mexc_data
from exchanges.bybit import get_bybit_data
from exchanges.gate import get_gate_data
from exchanges.bingx import get_bingx_data
from config import EXCHANGES

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log.txt", mode='w'),
        logging.StreamHandler()
    ]
)

def get_all_symbols(exchange):
    try:
        if exchange == "Binance":
            url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
            response = requests.get(url).json()
            symbols = [symbol["symbol"] for symbol in response["symbols"] if symbol["contractType"] == "PERPETUAL"]
            logging.info(f"Bin | Binance: fetched {len(symbols)} perpetual symbols: {symbols}")
            return symbols
        
        elif exchange == "MEXC":
            ticker_url = "https://contract.mexc.com/api/v1/contract/ticker"
            ticker_response = requests.get(ticker_url).json()
            time.sleep(0.5)  # Додано затримку для MEXC
            if not ticker_response.get("success"):
                logging.error(f"MEXC: failed to fetch ticker data, response: {ticker_response}")
                return []
            symbols = [ticker["symbol"].replace("_USDT", "USDT").replace("-USDT", "USDT") 
                      for ticker in ticker_response["data"]]
            logging.info(f"MEXC: fetched {len(symbols)} USDT contracts: {symbols}")
            return symbols
        
        elif exchange == "Bybit":
            url = "https://api.bybit.com/v5/market/tickers?category=linear"
            response = requests.get(url).json()
            if response["retCode"] != 0:
                logging.error(f"Bybit: failed to fetch ticker data, response: {response}")
                return []
            symbols = [item["symbol"] for item in response["result"]["list"]]
            logging.info(f"Bybit: fetched {len(symbols)} USDT contracts: {symbols}")
            return symbols
        
        elif exchange == "Gate.io":
            url = "https://api.gateio.ws/api/v4/futures/usdt/contracts"
            response = requests.get(url).json()
            time.sleep(0.5)  # Додано затримку для Gate.io
            symbols = [contract["name"] for contract in response]
            logging.info(f"Gate.io: fetched {len(symbols)} USDT contracts: {symbols}")
            return symbols
        
        elif exchange == "BingX":
            url = "https://open-api.bingx.com/openApi/swap/v2/quote/contracts"
            response = requests.get(url).json()
            time.sleep(0.5)  # Додано затримку для BingX
            logging.info(f"BingX API response: {response}")
            if response["code"] != 0:
                logging.error(f"BingX: failed to fetch ticker data, response: {response}")
                return []
            symbols = [item["symbol"] for item in response["data"]]
            logging.info(f"BingX: fetched {len(symbols)} USDT contracts: {symbols}")
            return symbols
                
    except Exception as e:
        logging.error(f"Error fetching symbols from {exchange}: {e}")
        time.sleep(1)
        return []

def fetch_symbols_for_exchange(exchange):
    symbols = get_all_symbols(exchange)
    if symbols is None:
        logging.warning(f"get_all_symbols returned None for {exchange}, returning empty list")
        symbols = []
    return exchange, symbols

def fetch_funding_for_symbol(exchange, symbol):
    try:
        if exchange == "Binance":
            url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
            response = requests.get(url).json()
            funding_rate = float(response["lastFundingRate"]) * 100
            mark_price = float(response["markPrice"])
            next_funding_time = datetime.fromtimestamp(response["nextFundingTime"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            
            result = {
                "Exchange": "Binance",
                "Symbol": symbol,
                "Next Funding (%)": funding_rate,
                "Mark Price (USD)": mark_price,
                "Next Funding Time": next_funding_time
            }
            return result
        
        elif exchange == "MEXC":
            mexc_symbol = symbol if "_USDT" in symbol else symbol.replace("USDT", "_USDT")
            result = get_mexc_data(mexc_symbol)
            time.sleep(0.5)  # Додано затримку для MEXC
            return result
        
        elif exchange == "Bybit":
            result = get_bybit_data(symbol)
            return result
        
        elif exchange == "Gate.io":
            gate_symbol = symbol if "_USDT" in symbol else symbol.replace("USDT", "_USDT")
            result = get_gate_data(gate_symbol)
            time.sleep(0.5)  # Додано затримку для Gate.io
            return result
        
        elif exchange == "BingX":
            bingx_symbol = symbol if "-USDT" in symbol else symbol.replace("USDT", "-USDT")
            result = get_bingx_data(bingx_symbol)
            time.sleep(0.5)  # Додано затримку для BingX
            return result
        
        else:
            logging.warning(f"Exchange {exchange} is not supported in this mode")
            return None
    except Exception as e:
        logging.error(f"Error fetching funding for {symbol} on {exchange}: {e}")
        return None

def fetch_funding_data():
    data = []
    logging.info(f"Starting fetch for exchanges: {EXCHANGES}")

    exchange_symbols = {}
    for exchange in EXCHANGES:
        exchange, symbols = fetch_symbols_for_exchange(exchange)
        logging.info(f"Exchange {exchange} returned {len(symbols)} symbols: {symbols}")
        exchange_symbols[exchange] = symbols

    tasks = []
    with ThreadPoolExecutor(max_workers=5) as executor:  # Зменшено до 5 потоків
        for exchange, symbols in exchange_symbols.items():
            if not symbols:
                logging.info(f"Skipping {exchange} due to empty symbols list")
                continue
            for symbol in symbols:
                tasks.append(executor.submit(fetch_funding_for_symbol, exchange, symbol))
        
        for future in as_completed(tasks):
            result = future.result()
            if result:
                data.append(result)
            time.sleep(0.1)

    logging.info(f"Collected {len(data)} funding rate entries")
    logging.info(f"Raw data before DataFrame: {data}")
    
    df = pd.DataFrame(data) if data else None
    
    if df is not None and not df.empty:
        logging.info(f"DataFrame after creation:\n{df}")
    
    return df

def calculate_funding_spread(df):
    if df is None or df.empty:
        return None
    
    df["Symbol"] = df["Symbol"].str.replace("_USDT", "USDT").str.replace("-USDT", "USDT")
    df["Base Symbol"] = df["Symbol"].str.replace("USDT", "")
    
    spread_data = []
    base_symbols = df["Base Symbol"].unique()

    for base_symbol in base_symbols:
        symbol_data = df[df["Base Symbol"] == base_symbol]
        if symbol_data.empty or len(symbol_data) < 2:
            continue

        funding_rates = symbol_data.set_index("Exchange")["Next Funding (%)"]
        max_rate = funding_rates.max()
        min_rate = funding_rates.min()
        spread = max_rate - min_rate
        
        max_exchange = funding_rates.idxmax()
        min_exchange = funding_rates.idxmin()

        if max_exchange != min_exchange and spread > 0:
            spread_data.append({
                "Symbol": base_symbol,
                "Max Funding (%)": max_rate,
                "Max Exchange": max_exchange,
                "Min Funding (%)": min_rate,
                "Min Exchange": min_exchange,
                "Spread (%)": spread
            })

    spread_df = pd.DataFrame(spread_data) if spread_data else None
    if spread_df is not None and not spread_df.empty:
        spread_df = spread_df.sort_values(by="Spread (%)", ascending=False)  # Сортування спредів від більшого до меншого
    return spread_df

def save_to_excel(df, spread_df):
    # Збереження таблиці з фандінг-рейтами
    if df is not None and not df.empty:
        df = df.fillna({
            "Next Funding Time": "N/A",
            "Mark Price (USD)": 0.0
        })
        df["Next Funding (%)"] = pd.to_numeric(df["Next Funding (%)"], errors='coerce')
        df[["Symbol", "Next Funding (%)", "Exchange", "Mark Price (USD)", "Next Funding Time"]].to_excel("funding_rates.xlsx", index=False)
        logging.info("Funding rates saved to funding_rates.xlsx")
    else:
        logging.info("No funding rates to save to Excel")

    # Збереження таблиці зі спредами
    if spread_df is not None and not spread_df.empty:
        spread_df[["Symbol", "Max Funding (%)", "Max Exchange", "Min Funding (%)", "Min Exchange", "Spread (%)"]].to_excel("funding_spreads.xlsx", index=False)
        logging.info("Funding spreads saved to funding_spreads.xlsx")
    else:
        logging.info("No funding spreads to save to Excel")

def main():
    print("Збір даних про фандінг-рейти...")
    df = fetch_funding_data()
    
    if df is not None and not df.empty:
        spread_df = calculate_funding_spread(df)
        save_to_excel(df, spread_df)
        print("Дані збережено: funding_rates.xlsx (фандінг-рейти), funding_spreads.xlsx (спреди)")
    else:
        print("Немає даних для збереження.")
        logging.info("No funding rates collected.")

if __name__ == "__main__":
    main()