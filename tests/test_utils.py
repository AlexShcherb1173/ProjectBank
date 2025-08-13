import os
import sys
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (aggregate_cards, filter_transactions_by_date, get_currency_rates, get_greeting,
                       get_stock_prices, get_top_transactions, load_user_settings)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


@pytest.fixture
def mock_currency_api():
    with patch("utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"rates": {"USD": 0.01365, "EUR": 0.01148}}
        yield mock_get


@pytest.fixture
def mock_stock_api():
    with patch("utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"chart": {"result": [{"meta": {"regularMarketPrice": 150.12}}]}}
        yield mock_get


def test_get_greeting():
    assert get_greeting(datetime(2021, 1, 1, 6)) == "Доброе утро"
    assert get_greeting(datetime(2021, 1, 1, 13)) == "Добрый день"
    assert get_greeting(datetime(2021, 1, 1, 18)) == "Добрый вечер"
    assert get_greeting(datetime(2021, 1, 1, 2)) == "Доброй ночи"


def test_filter_transactions_by_date():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2021-12-01 10:00:00", "2021-12-15 12:00:00", "2021-12-31 23:59:59"]),
            "Сумма операции": [-100, -200, -300],
        }
    )
    start = datetime(2021, 12, 1)
    end = datetime(2021, 12, 15, 23, 59, 59)
    filtered = filter_transactions_by_date(df, start, end)
    assert len(filtered) == 2


def test_aggregate_cards():
    # Создаем тестовый DataFrame
    data = {
        "Номер карты": ["*1234", "*1234", "*5678", "*5678", "*9999"],
        "Сумма операции": [-100.0, -50.0, -200.0, -100.0, -300.0],
        "Кэшбэк": [1.0, 0.5, 2.0, 1.0, 3.0],
    }
    df = pd.DataFrame(data)

    result = aggregate_cards(df)

    # Проверяем, что функция вернула список с тремя словарями (по 3 картам)
    assert isinstance(result, list)
    assert len(result) == 3

    # Проверяем сумму по карте "*1234"
    card_1234 = next((c for c in result if c["last_digits"] == "1234"), None)
    assert card_1234 is not None
    assert card_1234["total_spent"] == 150.0  # 100 + 50
    assert card_1234["cashback"] == 1.5  # 1.0 + 0.5

    # Проверяем сумму по карте "*5678"
    card_5678 = next((c for c in result if c["last_digits"] == "5678"), None)
    assert card_5678 is not None
    assert card_5678["total_spent"] == 300.0  # 200 + 100
    assert card_5678["cashback"] == 3.0  # 2.0 + 1.0

    # Проверяем сумму по карте "*9999"
    card_9999 = next((c for c in result if c["last_digits"] == "9999"), None)
    assert card_9999 is not None
    assert card_9999["total_spent"] == 300.0
    assert card_9999["cashback"] == 3.0


def test_get_top_transactions():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2021-12-01", "2021-12-02", "2021-12-03"]),
            "Сумма операции": [-100, -500, -200],
            "Категория": ["A", "B", "C"],
            "Описание": ["Desc1", "Desc2", "Desc3"],
        }
    )
    result = get_top_transactions(df, top_n=2)
    assert len(result) == 2
    assert result[0]["amount"] >= result[1]["amount"]


def test_load_user_settings(tmp_path):
    settings_file = tmp_path / "user_settings.json"
    settings_file.write_text('{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}', encoding="utf-8")
    settings = load_user_settings(str(settings_file))
    assert settings["user_currencies"] == ["USD"]
    assert settings["user_stocks"] == ["AAPL"]


def test_get_currency_rates_offline(mock_currency_api):
    result = get_currency_rates(["USD", "EUR"])
    assert result == [
        {"currency": "USD", "rate": round(1 / 0.01365, 2)},
        {"currency": "EUR", "rate": round(1 / 0.01148, 2)},
    ]


def test_get_stock_prices_offline(mock_stock_api):
    result = get_stock_prices(["AAPL"])
    assert result == [{"stock": "AAPL", "price": 150.12}]
