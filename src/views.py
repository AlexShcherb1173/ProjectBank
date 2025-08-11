# views.py содержит главную функцию generate_report(date_str)

import json
import os
from datetime import datetime

from dotenv import load_dotenv

import utils

load_dotenv()  # загрузить переменные из .env

USER_SETTINGS_FILE = os.getenv("USER_SETTINGS_FILE")
TRANSACTIONS_FILE = os.getenv("TRANSACTIONS_FILE")

def generate_report(date_str: str) -> str:
    """Генерация итогового отчета за выбранный период."""
    # Преобразуем дату из строки
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # Приветствие
    greeting = utils.get_greeting(dt)

    # Загрузка данных
    df = utils.load_transactions(
        os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")), TRANSACTIONS_FILE)
    )

    # Диапазон дат
    start_date = dt.replace(day=1, hour=0, minute=0, second=0)
    end_date = dt
    df_filtered = utils.filter_transactions_by_date(df, start_date, end_date)

    # Карты
    cards_info = utils.aggregate_cards(df_filtered)

    # Топ-5 транзакций
    top_transactions = utils.get_top_transactions(df_filtered)

    # Настройки пользователя
    settings = utils.load_user_settings(
        os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")), USER_SETTINGS_FILE)
    )
    # Курсы валют
    currency_rates = utils.get_currency_rates(settings["user_currencies"])

    # Цены акций
    stock_prices = utils.get_stock_prices(settings["user_stocks"])

    # Формируем JSON
    result = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
