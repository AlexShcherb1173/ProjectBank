#
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# import json
# import pandas as pd
# from unittest.mock import patch, MagicMock
# from views import generate_report
# import pytest
# from datetime import datetime
#
#
# @pytest.fixture
# def sample_df():
#     data = {
#         "Дата операции": [
#             "31.12.2021 16:44:00", "31.12.2021 16:42:04", "31.12.2021 16:39:04",
#             "31.12.2021 15:44:39", "31.12.2021 01:23:42", "31.12.2021 00:12:53"
#         ],
#         "Номер карты": ["*7197", "*7197", "*7197", "*7197", "*5091", ""],
#         "Сумма операции": ["-160,89", "-64,00", "-118,12", "-78,05", "-564,00", "-800,00"],
#         "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Супермаркеты", "Различные товары", "Переводы"],
#         "Описание": ["Колхоз", "Колхоз", "Магнит", "Колхоз", "Ozon.ru", "Константин Л."]
#     }
#     return pd.DataFrame(data)
#
#
# @pytest.fixture
# def mock_user_settings(tmp_path):
#     settings = {
#         "user_currencies": ["USD", "EUR"],
#         "user_stocks": ["AAPL", "AMZN"]
#     }
#     settings_path = tmp_path / "user_settings.json"
#     settings_path.write_text(json.dumps(settings, ensure_ascii=False), encoding="utf-8")
#     return str(settings_path)
#
#
# @patch("utils.get_currency_rates")
# @patch("utils.get_stock_prices")
# @patch("utils.load_user_settings")
# def test_generate_report(mock_load_settings, mock_stock_prices, mock_currency_rates, sample_df, mock_user_settings):
#     mock_load_settings.return_value = {
#         "user_currencies": ["USD", "EUR"],
#         "user_stocks": ["AAPL", "AMZN"]
#     }
#     mock_currency_rates.return_value = [
#         {"currency": "USD", "rate": 73.21},
#         {"currency": "EUR", "rate": 87.08}
#     ]
#     mock_stock_prices.return_value = [
#         {"stock": "AAPL", "price": 150.12},
#         {"stock": "AMZN", "price": 3173.18}
#     ]
#
#     result_json = generate_report("2021-12-31 23:59:59", sample_df)
#     result = json.loads(result_json)
#
#     assert "greeting" in result
#     assert len(result["cards"]) == 2
#     assert len(result["top_transactions"]) == 5
#     assert result["currency_rates"][0]["currency"] == "USD"
#     assert result["stock_prices"][0]["stock"] == "AAPL"
#
#
# @patch("utils.get_currency_rates")
# @patch("utils.get_stock_prices")
# @patch("utils.load_user_settings")
# @patch("utils.logger")
# def test_logger_calls(mock_logger, mock_load_settings, mock_stock_prices, mock_currency_rates, sample_df):
#     mock_load_settings.return_value = {
#         "user_currencies": ["USD"],
#         "user_stocks": ["AAPL"]
#     }
#     mock_currency_rates.return_value = [{"currency": "USD", "rate": 73.21}]
#     mock_stock_prices.return_value = [{"stock": "AAPL", "price": 150.12}]
#
#     generate_report("2021-12-31 10:00:00", sample_df)
#
#     assert mock_logger.info.call_count >= 0  # можно усилить, если добавим логи в utils

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
        "Дата операции": [
            "31.12.2021 16:44:00",
            "31.12.2021 15:44:39",
            "30.12.2021 10:00:00",
            "29.12.2021 20:00:00",
            "28.12.2021 18:30:00",
        ],
        "Номер карты": ["*7197", "*7197", "*5091", "*5091", "*1111"],
        "Сумма операции": [-160.89, -78.05, -564.00, -800.00, -2000.00],
        "Категория": ["Супермаркеты", "Супермаркеты", "Различные товары", "Переводы", "ЖКХ"],
        "Описание": ["Колхоз", "Колхоз", "Ozon.ru", "Константин Л.", "ЖКУ Квартира"]
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