# Как это работает
# @pytest.fixture создаёт тестовые данные, которые удобно переиспользовать.
# @patch("services.logging") заменяет модуль logging в services на мок-объект.
# Через mock_logging.info.assert_any_call(...) проверяем, что логгер вызван с нужным сообщением.
# Проверяем, что поиск работает корректно.

import json
import os
import sys

import pytest

from src.services import simple_search

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


@pytest.fixture
def sample_transactions():
    return [
        {"Описание": "Переводы Константин Л.", "Категория": "Переводы", "Сумма": -800},
        {"Описание": "Магазин Колхоз", "Категория": "Супермаркеты", "Сумма": -160.89},
        {"Описание": "Ozon.ru", "Категория": "Различные товары", "Сумма": -564},
        {"Описание": None, "Категория": 123, "Сумма": -50},  # проверка нестроковых полей
        "Это строка вместо словаря",  # проверка неправильного элемента
    ]


def test_simple_search_found(sample_transactions):
    query = "колхоз"
    result_json = simple_search(query, sample_transactions)
    results = json.loads(result_json)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["Категория"] == "Супермаркеты"


def test_simple_search_case_insensitive(sample_transactions):
    query = "переводы"
    result_json = simple_search(query, sample_transactions)
    results = json.loads(result_json)
    assert len(results) == 1
    assert results[0]["Категория"] == "Переводы"


def test_simple_search_no_query(sample_transactions):
    result_json = simple_search("", sample_transactions)
    results = json.loads(result_json)
    assert results == []


def test_simple_search_no_match(sample_transactions):
    query = "не найдено"
    result_json = simple_search(query, sample_transactions)
    results = json.loads(result_json)
    assert results == []


def test_simple_search_handles_non_dict(sample_transactions):
    # Элемент списка, который не dict, не вызывает ошибку и игнорируется
    query = "магазин"
    result_json = simple_search(query, sample_transactions)
    results = json.loads(result_json)
    assert any("Магазин" in tx.get("Описание", "") for tx in results)
