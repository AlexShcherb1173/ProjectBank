# utils.py — набор вспомогательных функций: приветствие, фильтрация по дате, агрегирование по картам,
# топ-транзакции, запрос валют и акций.
# user_settings.json — хранит валюты и акции.
# Будем использовать requests для API валют и акций, pandas для обработки транзакций, logging
# для отладки, json для сборки ответа.

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()  # загрузить переменные из .env

CURRENCY_API_BASE_URL = os.getenv("CURRENCY_API_BASE_URL")
STOCK_API_BASE_URL = os.getenv("STOCK_API_BASE_URL")


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


def aggregate_cards(df: pd.DataFrame) -> list[Dict]:
    """Функция суммирования трат и кэшбэка по картам с формированием отчета"""
    cards_info = []
    # Группируем по карте, суммируя и операции, и кэшбэк
    grouped = df.groupby("Номер карты").agg({"Сумма операции": "sum", "Кэшбэк": "sum"}).reset_index()

    for _, row in grouped.iterrows():
        card_num = str(row["Номер карты"])[-4:]
        total_spent = abs(row["Сумма операции"])
        cashback = round(row["Кэшбэк"], 2) if not pd.isna(row["Кэшбэк"]) else 0.0
        cards_info.append({"last_digits": card_num, "total_spent": round(total_spent, 2), "cashback": cashback})
    return cards_info


def get_top_transactions(df: pd.DataFrame, top_n: int = 5) -> list[Dict]:
    """Функция отбора транзакций по убыванию суммы"""
    df_sorted = df.sort_values(by="Сумма операции", key=abs, ascending=False).head(top_n)
    transactions = []
    for _, row in df_sorted.iterrows():
        transactions.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": abs(row["Сумма операции"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    return transactions


def load_user_settings(settings_path: str) -> dict:
    """Служебная функция для загрузки из файла пользовательских установок по валютам и акциям"""
    with open(settings_path, "r", encoding="utf-8") as f:
        data: dict[Any, Any] = json.load(f)
        return data


def get_currency_rates(currencies: list) -> list:
    """Функция получения курса валют"""
    url = f"{CURRENCY_API_BASE_URL}/RUB"
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
        url = f"{STOCK_API_BASE_URL}/{stock}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            json_data = response.json()
            price = json_data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            result.append({"stock": stock, "price": round(price, 2)})
        except Exception as e:
            logging.error(f"Ошибка получения цены {stock}: {e}")
    return result
