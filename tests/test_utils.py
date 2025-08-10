# Что здесь проверяется:
# Каждая функция в utils.py проверяется на то, что она вызывает logger.info() с ожидаемыми сообщениями.
# Для функций с переменными параметрами тест не проверяет полное совпадение строки, а ищет ключевые слова
# ("Отобрано", "кешбэк", "Выбрано" и т. д.).
# Все внешние зависимости (requests.get, open) замоканы, чтобы тесты были быстрыми и изолированными.

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import json
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest
import utils

@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Категория": "Супермаркеты",
            "Описание": "Колхоз",
            "Сумма операции": "-160.89",
            "Номер карты": "1234567812345678"
        },
        {
            "Дата операции": "31.12.2021 01:23:42",
            "Категория": "Различные товары",
            "Описание": "Ozon.ru",
            "Сумма операции": "-564.00",
            "Номер карты": "9876543298765432"
        }
    ])


@patch("utils.logger")
def test_get_greeting_logging(mock_logger):
    dt = datetime(2021, 12, 31, 9, 0, 0)
    utils.get_greeting(dt)
    mock_logger.info.assert_any_call("Определение приветствия для времени: 9:00")


@patch("utils.logger")
def test_filter_transactions_logging(mock_logger, sample_df):
    start = datetime(2021, 12, 31, 0, 0, 0)
    end = datetime(2021, 12, 31, 23, 59, 59)
    utils.filter_transactions(sample_df.copy(), start, end)
    mock_logger.info.assert_any_call(f"Фильтрация транзакций с {start} по {end}")
    assert any("Отобрано" in str(call.args[0]) for call in mock_logger.info.call_args_list)


@patch("utils.logger")
def test_summarize_cards_logging(mock_logger, sample_df):
    utils.summarize_cards(sample_df.copy())
    mock_logger.info.assert_any_call("Суммирование трат по картам")
    assert any("кешбэк" in str(call.args[0]) for call in mock_logger.info.call_args_list)


@patch("utils.logger")
def test_get_top_transactions_logging(mock_logger, sample_df):
    utils.get_top_transactions(sample_df.copy(), top_n=1)
    assert any("Определение топ" in str(call.args[0]) for call in mock_logger.info.call_args_list)
    assert any("Выбрано" in str(call.args[0]) for call in mock_logger.info.call_args_list)


@patch("utils.requests.get")
@patch("utils.logger")
def test_get_currency_rates_logging(mock_logger, mock_get):
    mock_get.return_value.json.return_value = {"rates": {"USD": 0.013}}
    utils.get_currency_rates(["USD"])
    mock_logger.info.assert_any_call("Получение курсов валют: ['USD']")
    assert any("Курсы валют получены" in str(call.args[0]) for call in mock_logger.info.call_args_list)


@patch("utils.requests.get")
@patch("utils.logger")
def test_get_stock_prices_logging(mock_logger, mock_get):
    mock_get.return_value.json.return_value = {
        "quoteResponse": {"result": [{"regularMarketPrice": 150.12}]}
    }
    utils.get_stock_prices(["AAPL"])
    mock_logger.info.assert_any_call("Получение котировок акций: ['AAPL']")
    assert any("Котировки получены" in str(call.args[0]) for call in mock_logger.info.call_args_list)


@patch("builtins.open", new_callable=MagicMock)
@patch("utils.logger")
def test_load_user_settings_logging(mock_logger, mock_open):
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({"key": "value"})
    utils.load_user_settings("fake_path.json")
    mock_logger.info.assert_any_call("Загрузка пользовательских настроек из fake_path.json")
    assert any("Настройки загружены" in str(call.args[0]) for call in mock_logger.info.call_args_list)