import json
import logging
import pandas as pd
from datetime import datetime
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

def get_greeting(date_obj: datetime) -> str:
    hour = date_obj.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def filter_transactions_by_date(df: pd.DataFrame, date_obj: datetime) -> pd.DataFrame:
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format="%d.%m.%Y %H:%M:%S")
    start_of_month = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return df[(df['Дата операции'] >= start_of_month) & (df['Дата операции'] <= date_obj)]

def get_cards_info(df: pd.DataFrame) -> list:
    cards_info = []
    for card_number, group in df.groupby('Номер карты'):
        if not card_number or not isinstance(card_number, str):
            continue
        last_digits = card_number[-4:]
        total_spent = group['Сумма операции'].sum()
        cashback = round(abs(total_spent) * 0.01, 2)  # 1 рубль на 100
        cards_info.append({
            "last_digits": last_digits,
            "total_spent": round(abs(total_spent), 2),
            "cashback": cashback
        })
    return cards_info

def get_top_transactions(df: pd.DataFrame, n=5) -> list:
    df_sorted = df.sort_values(by='Сумма платежа', key=abs, ascending=False).head(n)
    return [
        {
            "date": row['Дата операции'].strftime("%d.%m.%Y"),
            "amount": row['Сумма платежа'],
            "category": row['Категория'],
            "description": row['Описание']
        }
        for _, row in df_sorted.iterrows()
    ]

def get_user_settings(settings_path: str = "user_settings.json") -> dict:
    with open(settings_path, encoding="utf-8") as f:
        return json.load(f)

def get_currency_rates(currencies: list) -> list:
    url = "https://api.exchangerate.host/latest"
    response = requests.get(url, params={"base": "RUB"})
    response.raise_for_status()
    data = response.json()
    return [
        {"currency": cur, "rate": round(1 / data["rates"][cur], 2)}
        for cur in currencies if cur in data["rates"]
    ]

def get_stock_prices(stocks: list) -> list:
    # Для примера — подставные данные, в реальности использовать API Yahoo Finance / Polygon и т.д.
    return [
        {"stock": stock, "price": round(100 + i * 50.5, 2)}
        for i, stock in enumerate(stocks)
    ]
def load_user_settings(path="user_settings.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)