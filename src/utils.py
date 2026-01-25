# utils.py — набор вспомогательных функций: приветствие, фильтрация по дате, агрегирование по картам,
# топ-транзакции, запрос валют и акций.
# user_settings.json — хранит валюты и акции.
# Будем использовать requests для API валют и акций, pandas для обработки транзакций, logging
# для отладки, json для сборки ответа.

import json
import logging
import os
import requests
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import pandas as pd

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()  # загрузить переменные из .env

CURRENCY_API_BASE_URL = os.getenv("CURRENCY_API_BASE_URL")
STOCK_API_BASE_URL = os.getenv("STOCK_API_BASE_URL")

if not CURRENCY_API_BASE_URL:
    logging.warning("CURRENCY_API_BASE_URL is not set (.env)")
if not STOCK_API_BASE_URL:
    logging.warning("STOCK_API_BASE_URL is not set (.env)")

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


BASE_DIR = Path(__file__).resolve().parents[1]

def load_transactions(path: str) -> pd.DataFrame:
    file_path = BASE_DIR / path

    if file_path.suffix == ".xlsx":
        return pd.read_excel(file_path)
    elif file_path.suffix == ".csv":
        return pd.read_csv(file_path)
    elif file_path.suffix == ".json":
        return pd.read_json(file_path)

    raise ValueError("Unsupported file format")

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


def get_currency_rates(currencies: list[str], base: str = "RUB") -> list[dict]:
    """Получение курсов валют относительно base."""
    if not CURRENCY_API_BASE_URL:
        raise RuntimeError("CURRENCY_API_BASE_URL is not set in .env")

    # ожидаем, что base url = "https://api.exchangerate.host/latest"
    response = requests.get(
        CURRENCY_API_BASE_URL,
        params={"base": base, "symbols": ",".join(currencies)},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    rates = data.get("rates", {})
    result = []
    for cur in currencies:
        rate = rates.get(cur)
        if rate is not None:
            result.append({"currency": cur, "rate": round(rate, 4)})  # 1 RUB -> cur
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
