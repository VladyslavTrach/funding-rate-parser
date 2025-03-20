# main.py
import pandas as pd
from data_fetcher import fetch_funding_data, calculate_funding_spread
from bot import run_bot

def main():
    """Основна функція для запуску у консолі."""
    # data = fetch_funding_data()
    # if data is not None:
    #     print("\nРезультати:")
    #     print(data)
    #     data.to_csv("funding_rates.csv", index=False)

    # spread_data = calculate_funding_spread(data)
    # if spread_data is not None:
    #     print("\nСпред фандінг-рейтів між біржами:")
    #     print(spread_data)
    #     spread_data.to_csv("funding_spread.csv", index=False)
    #     print("Дані збережено у 'funding_rates.csv' та 'funding_spread.csv'")
    # else:
    #     print("Дані збережено у 'funding_rates.csv'")

    # Запускаємо бота
    run_bot()

if __name__ == "__main__":
    main()