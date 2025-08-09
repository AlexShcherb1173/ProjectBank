# Как это работает
# @pytest.fixture создаёт тестовые данные, которые удобно переиспользовать.
# @patch("services.logging") заменяет модуль logging в services на мок-объект.
# Через mock_logging.info.assert_any_call(...) проверяем, что логгер вызван с нужным сообщением.
# Проверяем, что поиск работает корректно.

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import json
import pytest
from unittest.mock import patch
from src.services import simple_search

@pytest.fixture
def sample_transactions():
    return [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Категория": "Супермаркеты",
            "Описание": "Колхоз",
            "Сумма операции": -160.89,
        },
        {
            "Дата операции": "31.12.2021 16:42:04",
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
            "Сумма операции": -64.00,
        },
        {
            "Дата операции": "31.12.2021 01:23:42",
            "Категория": "Различные товары",
            "Описание": "Ozon.ru",
            "Сумма операции": -564.00,
        },
    ]

@patch("services.logging.info")
def test_search_by_description(mock_logging, sample_transactions):
    result_json = simple_search("Колхоз", sample_transactions)
    result = json.loads(result_json)

    # Проверяем результат поиска
    assert len(result) == 1
    assert result[0]["Описание"] == "Колхоз"

    # Проверяем, что логгер вызвался минимум 2 раза (info о начале и конце)
    assert mock_logging.call_count == 2
    mock_logging.assert_any_call("Начат поиск по запросу: 'Колхоз'")
    mock_logging.assert_any_call("Найдено 1 транзакций по запросу 'Колхоз'")

@patch("services.logging.info")
def test_search_case_insensitive(mock_logging, sample_transactions):
    result_json = simple_search("ozon", sample_transactions)
    result = json.loads(result_json)
    assert len(result) == 1
    assert result[0]["Описание"] == "Ozon.ru"

    assert mock_logging.call_count == 2

@patch("services.logging.warning")
def test_search_empty_query(mock_logging, sample_transactions):
    result_json = simple_search("", sample_transactions)
    result = json.loads(result_json)
    assert result == []

    # Проверка вызова warning для пустого запроса
    mock_logging.assert_called_once_with("Пустой поисковый запрос")