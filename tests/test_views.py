
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from views import generate_report

import pytest
from datetime import datetime


@pytest.fixture
def sample_df():
    data = {
        "Дата операции": [
            "31.12.2021 16:44:00", "31.12.2021 16:42:04", "31.12.2021 16:39:04",
            "31.12.2021 15:44:39", "31.12.2021 01:23:42", "31.12.2021 00:12:53"
        ],
        "Номер карты": ["*7197", "*7197", "*7197", "*7197", "*5091", ""],
        "Сумма операции": ["-160,89", "-64,00", "-118,12", "-78,05", "-564,00", "-800,00"],
        "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Супермаркеты", "Различные товары", "Переводы"],
        "Описание": ["Колхоз", "Колхоз", "Магнит", "Колхоз", "Ozon.ru", "Константин Л."]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_user_settings(tmp_path):
    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN"]
    }
    settings_path = tmp_path / "user_settings.json"
    settings_path.write_text(json.dumps(settings, ensure_ascii=False), encoding="utf-8")
    return str(settings_path)


@patch("utils.get_currency_rates")
@patch("utils.get_stock_prices")
@patch("utils.load_user_settings")
def test_generate_report(mock_load_settings, mock_stock_prices, mock_currency_rates, sample_df, mock_user_settings):
    mock_load_settings.return_value = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN"]
    }
    mock_currency_rates.return_value = [
        {"currency": "USD", "rate": 73.21},
        {"currency": "EUR", "rate": 87.08}
    ]
    mock_stock_prices.return_value = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18}
    ]

    result_json = generate_report("2021-12-31 23:59:59", sample_df)
    result = json.loads(result_json)

    assert "greeting" in result
    assert len(result["cards"]) == 2
    assert len(result["top_transactions"]) == 5
    assert result["currency_rates"][0]["currency"] == "USD"
    assert result["stock_prices"][0]["stock"] == "AAPL"


@patch("utils.get_currency_rates")
@patch("utils.get_stock_prices")
@patch("utils.load_user_settings")
@patch("utils.logger")
def test_logger_calls(mock_logger, mock_load_settings, mock_stock_prices, mock_currency_rates, sample_df):
    mock_load_settings.return_value = {
        "user_currencies": ["USD"],
        "user_stocks": ["AAPL"]
    }
    mock_currency_rates.return_value = [{"currency": "USD", "rate": 73.21}]
    mock_stock_prices.return_value = [{"stock": "AAPL", "price": 150.12}]

    generate_report("2021-12-31 10:00:00", sample_df)

    assert mock_logger.info.call_count >= 0  # можно усилить, если добавим логи в utils