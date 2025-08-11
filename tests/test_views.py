import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import json
import pytest
from unittest.mock import patch
import views
import pandas as pd
from datetime import datetime


@pytest.fixture
def sample_df():
    data = {
    "Дата операции": pd.to_datetime([
        "2021-12-31 16:44:00",
        "2021-12-31 15:44:39",
        "2021-12-28 18:30:00",
        "2021-12-20 10:00:00"
    ]),
    "Номер карты": ["*7197", "*7197", "*1111", "*1111"],
    "Сумма операции": [-160.89, -78.05, -564.00, -50.00],
    "Кэшбэк": [3.00, 1.00, 5.00, 0.50],
    "Категория": ["Супермаркеты", "Супермаркеты", "Различные товары", "Супермаркеты"],
    "Описание": ["Колхоз", "Колхоз", "Ozon.ru", "Магазин"]
}
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return df


def mock_currency_rates(_):
    return [
        {"currency": "USD", "rate": 73.21},
        {"currency": "EUR", "rate": 87.08}
    ]


def mock_stock_prices(_):
    return [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08}
    ]


def mock_user_settings(_):
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    }


@patch("utils.load_transactions")
@patch("utils.get_currency_rates", side_effect=mock_currency_rates)
@patch("utils.get_stock_prices", side_effect=mock_stock_prices)
@patch("utils.load_user_settings", side_effect=mock_user_settings)
def test_generate_report(mock_settings, mock_stocks, mock_currencies, mock_load_df, sample_df):
    mock_load_df.return_value = sample_df

    result_json = views.generate_report("2021-12-31 16:00:00")
    result = json.loads(result_json)

    # Общая структура
    assert set(result.keys()) == {
        "greeting", "cards", "top_transactions", "currency_rates", "stock_prices"
    }

    # Приветствие
    assert result["greeting"] in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]

    # Карты
    assert isinstance(result["cards"], list)
    assert all("last_digits" in card for card in result["cards"])

    # Топ транзакций
    assert len(result["top_transactions"]) <= 5
    assert all("amount" in tx for tx in result["top_transactions"])

    # Валюты
    assert result["currency_rates"][0]["currency"] == "USD"

    # Акции
    assert result["stock_prices"][0]["stock"] == "AAPL"