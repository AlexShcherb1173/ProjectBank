# views.py содержит главную функцию generate_report(date_str)
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src import utils  # <-- нормальный импорт

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]  # .../ProjectBank
DATA_DIR = BASE_DIR / "data"

USER_SETTINGS_FILE = os.getenv("USER_SETTINGS_FILE", "user_settings.json")
TRANSACTIONS_FILE = os.getenv("TRANSACTIONS_FILE", "operations.xlsx")


def generate_report(date_str: str) -> str:
    """Генерация итогового отчета за выбранный период."""
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    greeting = utils.get_greeting(dt)

    # Файл транзакций
    transactions_path = DATA_DIR / TRANSACTIONS_FILE
    if not transactions_path.exists():
        raise FileNotFoundError(f"Transactions file not found: {transactions_path}")

    df = utils.load_transactions(str(transactions_path))

    start_date = dt.replace(day=1, hour=0, minute=0, second=0)
    end_date = dt
    df_filtered = utils.filter_transactions_by_date(df, start_date, end_date)

    cards_info = utils.aggregate_cards(df_filtered)
    top_transactions = utils.get_top_transactions(df_filtered)

    # Файл настроек
    settings_path = BASE_DIR / USER_SETTINGS_FILE
    if not settings_path.exists():
        raise FileNotFoundError(f"User settings file not found: {settings_path}")

    settings = utils.load_user_settings(str(settings_path))

    currency_rates = utils.get_currency_rates(settings["user_currencies"])
    stock_prices = utils.get_stock_prices(settings["user_stocks"])

    result = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)