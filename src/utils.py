# Модуль utils содержит вспомогательные функции для модуля views

# import json
# import logging
# import requests
# from datetime import datetime
# import pandas as pd
#
# logger = logging.getLogger(__name__)
#
# def get_greeting(dt: datetime) -> str:
#     """Функция - приветствие для пользователя в зависимости от времени суток"""
#     hour = dt.hour
#     logger.info(f"Определение приветствия для времени: {hour}:00")
#     if 5 <= hour < 12:
#         return "Доброе утро"
#     elif 12 <= hour < 18:
#         return "Добрый день"
#     elif 18 <= hour < 23:
#         return "Добрый вечер"
#     else:
#         return "Доброй ночи"
#
# def filter_transactions(df: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
#     """Функция фильтрации транзакций по картам по датам"""
#     logger.info(f"Фильтрация транзакций с {start} по {end}")
#     df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
#     filtered = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]
#     logger.info(f"Отобрано {len(filtered)} транзакций")
#     return filtered
#
# def summarize_cards(df: pd.DataFrame):
#     """Функция суммирования трат по картам с формированием отчета"""
#     logger.info("Суммирование трат по картам")
#     cards_summary = []
#     for card, group in df.groupby("Номер карты"):
#         if not card or not isinstance(card, str):
#             logger.info(f"Пропущена карта: {card}")
#             continue
#         total_spent = abs(group["Сумма операции"].astype(str).str.replace(",", ".").astype(float).sum())
#         cashback = round(total_spent / 100, 2)
#         logger.info(f"Карта {card[-4:]}: потрачено {total_spent}, кешбэк {cashback}")
#         cards_summary.append({
#             "last_digits": card[-4:],
#             "total_spent": round(total_spent, 2),
#             "cashback": cashback
#         })
#     return cards_summary
#
# def get_top_transactions(df: pd.DataFrame, top_n=5):
#     """Функция отбора транзакций по убыванию суммы"""
#     logger.info(f"Определение топ-{top_n} транзакций по сумме")
#     df["Сумма операции"] = df["Сумма операции"].astype(str).str.replace(",", ".").astype(float)
#     top = df.sort_values(by="Сумма операции", key=abs, ascending=False).head(top_n)
#     logger.info(f"Выбрано {len(top)} транзакций")
#     return [
#         {
#             "date": row["Дата операции"].strftime("%d.%m.%Y"),
#             "amount": row["Сумма операции"],
#             "category": row["Категория"],
#             "description": row["Описание"]
#         }
#         for _, row in top.iterrows()
#     ]
#
# def get_currency_rates(currencies):
#     """Функция получения курса валют"""
#     logger.info(f"Получение курсов валют: {currencies}")
#     url = f"https://api.exchangerate.host/latest?base=RUB"
#     response = requests.get(url)
#     data = response.json()
#     result = [{"currency": cur, "rate": round(1 / data["rates"][cur], 2)} for cur in currencies]
#     logger.info(f"Курсы валют получены: {result}")
#     return result
#
# def get_stock_prices(stocks):
#     """Функция получения котировок акций"""
#     logger.info(f"Получение котировок акций: {stocks}")
#     prices = []
#     for stock in stocks:
#         url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}"
#         r = requests.get(url)
#         data = r.json()
#         price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
#         prices.append({"stock": stock, "price": round(price, 2)})
#     logger.info(f"Котировки получены: {prices}")
#     return prices
#
# def load_user_settings(path="user_settings.json"):
#     """Служебная функция для загрузки из файла пользовательских установок по валютам и акциям"""
#     logger.info(f"Загрузка пользовательских настроек из {path}")
#     with open(path, "r", encoding="utf-8") as f:
#         settings = json.load(f)
#     logger.info(f"Настройки загружены: {settings}")
#     return settings


import json
import logging
import pandas as pd
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def get_greeting(dt: datetime) -> str:
    """Функция - приветствие для пользователя в зависимости от времени суток"""
    hour = dt.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def load_transactions(file_path: str) -> pd.DataFrame:
    """Функция создает DataFrame из xlsx файла"""
    df = pd.read_excel(file_path)
    return df

def filter_transactions_by_date(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Функция фильтрации транзакций по датам"""
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    return df.loc[mask]

def aggregate_cards(df: pd.DataFrame):
    """Функция суммирования трат по картам с формированием отчета"""
    cards_info = []
    grouped = df.groupby("Номер карты")["Сумма операции"].sum().reset_index()
    for _, row in grouped.iterrows():
        card_num = str(row["Номер карты"])[-4:]
        total_spent = abs(row["Сумма операции"])
        cashback = round(total_spent / 100, 2)
        cards_info.append({
            "last_digits": card_num,
            "total_spent": round(total_spent, 2),
            "cashback": cashback
        })
    return cards_info

def get_top_transactions(df: pd.DataFrame, top_n: int = 5):
    """Функция отбора транзакций по убыванию суммы"""
    df_sorted = df.sort_values(by="Сумма операции", key=abs, ascending=False).head(top_n)
    transactions = []
    for _, row in df_sorted.iterrows():
        transactions.append({
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": abs(row["Сумма операции"]),
            "category": row["Категория"],
            "description": row["Описание"]
        })
    return transactions

def load_user_settings(settings_path: str) -> dict:
    """Служебная функция для загрузки из файла пользовательских установок по валютам и акциям"""
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_currency_rates(currencies: list) -> list:
    """Функция получения курса валют"""
    url = "https://open.er-api.com/v6/latest/RUB"
    response = requests.get(url)
    data = response.json()
    result = []
    for cur in currencies:
        if cur in data["rates"]:
            result.append({"currency": cur, "rate": round(1 / data["rates"][cur], 2)})
    return result

def get_stock_prices(stocks: list) -> list:
    """Функция получения котировок акций"""
    # Здесь пример с Yahoo Finance API (через yfinance можно улучшить)
    result = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for stock in stocks:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            json_data = response.json()
            price = json_data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            result.append({"stock": stock, "price": round(price, 2)})
        except Exception as e:
            logging.error(f"Ошибка получения цены {stock}: {e}")
    return result
