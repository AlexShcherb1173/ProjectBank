# Реализация функции сервиса «Простой поиск» в модуле services.py, которая принимает строку запроса и
# список транзакций (список словарей), ищет совпадения в полях "Описание" и "Категория",
# логирует процесс и возвращает JSON-ответ с найденными транзакциями

# Что делает функция
# Логирует начало поиска.
# Если запрос пустой — возвращает пустой список.
# Ищет все транзакции, где query содержится в "Описание" или "Категория" (без учёта регистра).
# Логирует сколько найдено совпадений.
# Возвращает результат в формате JSON с красивым форматированием (indent=4).
# Использует ensure_ascii=False, чтобы русский текст не превратился в escape-последовательности.

import json
import logging
from typing import Any, Dict, List


def simple_search(query: str, transactions: List[Dict]) -> str:
    """
    Поиск транзакций, где query содержится в 'Описание' или 'Категория' (регистронезависимо).
    Возвращает JSON-строку с найденными транзакциями.

    :param query: строка для поиска
    :param transactions: список словарей с транзакциями
    :return: JSON строка с найденными записями
    """
    logging.info(f"Начат поиск по запросу: '{query}'")

    if not query:
        logging.warning("Пустой поисковый запрос")
        result: list[Any] = []
    else:
        lower_query = query.lower()
        result = []
        for tx in transactions:
            if not isinstance(tx, dict):
                continue
            description = str(tx.get("Описание", "")).lower()
            category = str(tx.get("Категория", "")).lower()
            if (lower_query in description) or (lower_query in category):
                result.append(tx)

    logging.info(f"Найдено {len(result)} транзакций по запросу '{query}'")
    return json.dumps(result, ensure_ascii=False, indent=4)
