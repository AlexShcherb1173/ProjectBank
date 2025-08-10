# views.py будет содержать главную функцию generate_report(date_str, df)
# utils.py — набор вспомогательных функций: приветствие, фильтрация по дате, агрегирование по картам, топ-транзакции, запрос валют и акций.
# user_settings.json — хранит валюты и акции.
# Будем использовать requests для API валют и акций, pandas для обработки транзакций, logging
# для отладки, json для сборки ответа.


import json
import logging
from datetime import datetime
from utils import (
    get_greeting,
    filter_transactions_by_date,
    get_cards_info,
    get_top_transactions,
    get_user_settings,
    get_currency_rates,
    get_stock_prices
)

logger = logging.getLogger(__name__)


def generate_report(date_str: str, df) -> str:
    logger.info("Начало генерации отчета")

    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    df_filtered = filter_transactions_by_date(df, date_obj)

    greeting = get_greeting(date_obj)
    cards_info = get_cards_info(df_filtered)
    top_transactions = get_top_transactions(df_filtered)

    settings = get_user_settings()
    currency_rates = get_currency_rates(settings["user_currencies"])
    stock_prices = get_stock_prices(settings["user_stocks"])

    result = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    logger.info("Отчет успешно сгенерирован")
    return json.dumps(result, ensure_ascii=False, indent=2)


