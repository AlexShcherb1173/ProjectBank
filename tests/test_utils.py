# Что тут есть:
# @patch("utils.logger") — мокает logger, чтобы проверить вызовы logger.info().
# @patch("utils.requests.get") — заменяет запросы к API фейковыми данными.
# mock_open — подменяет чтение файлов для load_user_settings.
# Проверка логов по ключевым фразам.
# Проверка корректности возвращаемых данных.
#
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# import pytest
# import pandas as pd
# from datetime import datetime
# from unittest.mock import patch, mock_open
# import json
# import builtins
# import utils
#
#
# @pytest.fixture
# def sample_df():
#     return pd.DataFrame({
#         "Дата операции": [
#             "31.12.2021 16:44:00",
#             "31.12.2021 15:44:39",
#             "01.01.2022 10:00:00"
#         ],
#         "Сумма операции": ["-160.89", "-78.05", "-200.00"],
#         "Номер карты": ["*7197", "*7197", "*1234"],
#         "Категория": ["Еда", "Еда", "Транспорт"],
#         "Описание": ["Покупка 1", "Покупка 2", "Поездка"]
#     })
#
#
# @patch("utils.logger")
# def test_get_greeting_logs(mock_logger):
#     result = utils.get_greeting(datetime(2021, 12, 31, 9, 0))
#     assert result == "Доброе утро"
#     mock_logger.info.assert_any_call("Определение приветствия для времени: 9:00")
#
#
# @patch("utils.logger")
# def test_filter_transactions_logs(mock_logger, sample_df):
#     start = datetime(2021, 12, 31, 0, 0, 0)
#     end = datetime(2021, 12, 31, 23, 59, 59)
#     result = utils.filter_transactions(sample_df.copy(), start, end)
#     assert len(result) == 2
#     calls = [c.args[0] for c in mock_logger.info.call_args_list]
#     assert any("Фильтрация транзакций" in msg for msg in calls)
#     assert any("Отобрано" in msg for msg in calls)
#
#
# @patch("utils.logger")
# def test_summarize_cards_logs(mock_logger, sample_df):
#     result = utils.summarize_cards(sample_df.copy())
#     assert isinstance(result, list)
#     calls = [c.args[0] for c in mock_logger.info.call_args_list]
#     assert any("Суммирование трат по картам" in msg for msg in calls)
#     assert any("Карта" in msg for msg in calls)
#
#
# @patch("utils.logger")
# def test_get_top_transactions_logs(mock_logger, sample_df):
#     sample_df["Дата операции"] = pd.to_datetime(sample_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
#     result = utils.get_top_transactions(sample_df.copy(), top_n=2)
#     assert len(result) == 2
#     calls = [c.args[0] for c in mock_logger.info.call_args_list]
#     assert any("Определение топ" in msg for msg in calls)
#     assert any("Выбрано" in msg for msg in calls)
#
#
# @patch("utils.requests.get")
# @patch("utils.logger")
# def test_get_currency_rates_logs(mock_logger, mock_get):
#     mock_get.return_value.json.return_value = {"rates": {"USD": 0.013, "EUR": 0.011}}
#     result = utils.get_currency_rates(["USD", "EUR"])
#     assert result == [
#         {"currency": "USD", "rate": round(1 / 0.013, 2)},
#         {"currency": "EUR", "rate": round(1 / 0.011, 2)}
#     ]
#     calls = [c.args[0] for c in mock_logger.info.call_args_list]
#     assert any("Получение курсов валют" in msg for msg in calls)
#     assert any("Курсы валют получены" in msg for msg in calls)
#
#
# @patch("utils.requests.get")
# @patch("utils.logger")
# def test_get_stock_prices_logs(mock_logger, mock_get):
#     mock_get.return_value.json.return_value = {
#         "quoteResponse": {
#             "result": [{"regularMarketPrice": 150.12}]
#         }
#     }
#     result = utils.get_stock_prices(["AAPL"])
#     assert result == [{"stock": "AAPL", "price": 150.12}]
#     calls = [c.args[0] for c in mock_logger.info.call_args_list]
#     assert any("Получение котировок акций" in msg for msg in calls)
#     assert any("Котировки получены" in msg for msg in calls)
#
#
# @patch("utils.logger")
# def test_load_user_settings_logs(mock_logger):
#     fake_data = {"theme": "dark", "language": "ru"}
#     m = mock_open(read_data=json.dumps(fake_data))
#     with patch.object(builtins, "open", m):
#         result = utils.load_user_settings("fake_path.json")
#     assert result == fake_data
#     calls = [c.args[0] for c in mock_logger.info.call_args_list]
#     assert any("Загрузка пользовательских настроек" in msg for msg in calls)
#     assert any("Настройки загружены" in msg for msg in calls)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import pandas as pd
from datetime import datetime
import utils
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_currency_api():
    with patch("utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "rates": {
                "USD": 0.01365,
                "EUR": 0.01148
            }
        }
        yield mock_get


@pytest.fixture
def mock_stock_api():
    with patch("utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "chart": {
                "result": [
                    {
                        "meta": {"regularMarketPrice": 150.12}
                    }
                ]
            }
        }
        yield mock_get


def test_get_greeting():
    assert utils.get_greeting(datetime(2021, 1, 1, 6)) == "Доброе утро"
    assert utils.get_greeting(datetime(2021, 1, 1, 13)) == "Добрый день"
    assert utils.get_greeting(datetime(2021, 1, 1, 18)) == "Добрый вечер"
    assert utils.get_greeting(datetime(2021, 1, 1, 2)) == "Доброй ночи"


def test_filter_transactions_by_date():
    df = pd.DataFrame({
        "Дата операции": pd.to_datetime([
            "2021-12-01 10:00:00", "2021-12-15 12:00:00", "2021-12-31 23:59:59"
        ]),
        "Сумма операции": [-100, -200, -300]
    })
    start = datetime(2021, 12, 1)
    end = datetime(2021, 12, 15, 23, 59, 59)
    filtered = utils.filter_transactions_by_date(df, start, end)
    assert len(filtered) == 2


def test_aggregate_cards():
    df = pd.DataFrame({
        "Номер карты": ["*1111", "*1111", "*2222"],
        "Сумма операции": [-100.0, -200.0, -300.0]
    })
    result = utils.aggregate_cards(df)
    assert any(card["last_digits"] == "1111" for card in result)
    assert any(card["last_digits"] == "2222" for card in result)


def test_get_top_transactions():
    df = pd.DataFrame({
        "Дата операции": pd.to_datetime([
            "2021-12-01", "2021-12-02", "2021-12-03"
        ]),
        "Сумма операции": [-100, -500, -200],
        "Категория": ["A", "B", "C"],
        "Описание": ["Desc1", "Desc2", "Desc3"]
    })
    result = utils.get_top_transactions(df, top_n=2)
    assert len(result) == 2
    assert result[0]["amount"] >= result[1]["amount"]


def test_load_user_settings(tmp_path):
    settings_file = tmp_path / "user_settings.json"
    settings_file.write_text('{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}', encoding="utf-8")
    settings = utils.load_user_settings(str(settings_file))
    assert settings["user_currencies"] == ["USD"]
    assert settings["user_stocks"] == ["AAPL"]


def test_get_currency_rates_offline(mock_currency_api):
    result = utils.get_currency_rates(["USD", "EUR"])
    assert result == [
        {"currency": "USD", "rate": round(1 / 0.01365, 2)},
        {"currency": "EUR", "rate": round(1 / 0.01148, 2)}
    ]


def test_get_stock_prices_offline(mock_stock_api):
    result = utils.get_stock_prices(["AAPL"])
    assert result == [{"stock": "AAPL", "price": 150.12}]