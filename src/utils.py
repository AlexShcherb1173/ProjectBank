import json
import logging
import requests
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

def get_greeting(dt: datetime) -> str:
    hour = dt.hour
    logger.info(f"Определение приветствия для времени: {hour}:00")
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def filter_transactions(df: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
    logger.info(f"Фильтрация транзакций с {start} по {end}")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]
    logger.info(f"Отобрано {len(filtered)} транзакций")
    return filtered

def summarize_cards(df: pd.DataFrame):
    logger.info("Суммирование трат по картам")
    cards_summary = []
    for card, group in df.groupby("Номер карты"):
        if not card or not isinstance(card, str):
            logger.info(f"Пропущена карта: {card}")
            continue
        total_spent = abs(group["Сумма операции"].astype(str).str.replace(",", ".").astype(float).sum())
        cashback = round(total_spent / 100, 2)
        logger.info(f"Карта {card[-4:]}: потрачено {total_spent}, кешбэк {cashback}")
        cards_summary.append({
            "last_digits": card[-4:],
            "total_spent": round(total_spent, 2),
            "cashback": cashback
        })
    return cards_summary

def get_top_transactions(df: pd.DataFrame, top_n=5):
    logger.info(f"Определение топ-{top_n} транзакций по сумме")
    df["Сумма операции"] = df["Сумма операции"].astype(str).str.replace(",", ".").astype(float)
    top = df.sort_values(by="Сумма операции", key=abs, ascending=False).head(top_n)
    logger.info(f"Выбрано {len(top)} транзакций")
    return [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"]
        }
        for _, row in top.iterrows()
    ]

def get_currency_rates(currencies):
    logger.info(f"Получение курсов валют: {currencies}")
    url = f"https://api.exchangerate.host/latest?base=RUB"
    response = requests.get(url)
    data = response.json()
    result = [{"currency": cur, "rate": round(1 / data["rates"][cur], 2)} for cur in currencies]
    logger.info(f"Курсы валют получены: {result}")
    return result

def get_stock_prices(stocks):
    logger.info(f"Получение котировок акций: {stocks}")
    prices = []
    for stock in stocks:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}"
        r = requests.get(url)
        data = r.json()
        price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
        prices.append({"stock": stock, "price": round(price, 2)})
    logger.info(f"Котировки получены: {prices}")
    return prices

def load_user_settings(path="user_settings.json"):
    logger.info(f"Загрузка пользовательских настроек из {path}")
    with open(path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    logger.info(f"Настройки загружены: {settings}")
    return settings