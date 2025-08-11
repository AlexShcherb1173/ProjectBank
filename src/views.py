# views.py будет содержать главную функцию generate_report(date_str, df)
# utils.py — набор вспомогательных функций: приветствие, фильтрация по дате, агрегирование по картам,
# топ-транзакции, запрос валют и акций.
# user_settings.json — хранит валюты и акции.
# Будем использовать requests для API валют и акций, pandas для обработки транзакций, logging
# для отладки, json для сборки ответа.

#
# import json
# import logging
# from datetime import datetime
# from utils import (
#     get_greeting,
#     filter_transactions,
#     summarize_cards,
#     get_top_transactions,
#     load_user_settings,
#     get_currency_rates,
#     get_stock_prices
# )
#
# logger = logging.getLogger(__name__)
#
#
# def generate_report(date_str: str, df) -> str:
#     """Генерация итогового отчета за выбранный период."""
#     logger.info("Начало генерации отчета")
#
#     date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
#     df_filtered = filter_transactions(df, date_obj)
#
#     greeting = get_greeting(date_obj)
#     cards_info = summarize_cards(df_filtered)
#     top_transactions = get_top_transactions(df_filtered)
#
#     settings = load_user_settings()
#     currency_rates = get_currency_rates(settings["user_currencies"])
#     stock_prices = get_stock_prices(settings["user_stocks"])
#
#     result = {
#         "greeting": greeting,
#         "cards": cards_info,
#         "top_transactions": top_transactions,
#         "currency_rates": currency_rates,
#         "stock_prices": stock_prices
#     }
#
#     logger.info("Отчет успешно сгенерирован")
#     return json.dumps(result, ensure_ascii=False, indent=2)


import json
from datetime import datetime
import utils

def generate_report(date_str: str) -> str:
    """Генерация итогового отчета за выбранный период."""
    # Преобразуем дату из строки
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # Приветствие
    greeting = utils.get_greeting(dt)

    # Загрузка данных
    df = utils.load_transactions("transactions.xlsx")

    # Диапазон дат
    start_date = dt.replace(day=1, hour=0, minute=0, second=0)
    end_date = dt
    df_filtered = utils.filter_transactions_by_date(df, start_date, end_date)

    # Карты
    cards_info = utils.aggregate_cards(df_filtered)

    # Топ-5 транзакций
    top_transactions = utils.get_top_transactions(df_filtered)

    # Настройки пользователя
    settings = utils.load_user_settings("user_settings.json")

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
        "stock_prices": stock_prices
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


