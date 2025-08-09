#Отчет траты по заданным категориям
# Что делает код
# Декоратор save_report перехватывает результат функции. Если результат — DataFrame, сохраняет его в .csv.
# Если имя файла не передано, генерирует по текущему времени.
# Функция-отчёт фильтрует DataFrame по: категории, диапазону дат (последние 90 дней)
# В логах выводится: категория отчёта, количество найденных транзакций, путь к сохранённому файлу.

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Union, Callable
import functools
import os

# ------------------ Декоратор ------------------
def save_report(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции-отчёта в CSV файл.
    :param filename: Имя файла (если None, создаётся автоматически по дате/времени)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if not isinstance(result, pd.DataFrame):
                raise TypeError("Функция-отчёт должна возвращать pandas.DataFrame")

            # Имя файла
            file_to_s = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_to_save = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'report')), file_to_s)

            # Сохраняем в CSV
            result.to_csv(file_to_save, index=False, encoding="utf-8-sig")

            logging.info(f"Отчёт сохранён в файл: {os.path.abspath(file_to_save)}")
            return result
        return wrapper

    # Если вызвали как @save_report без скобок
    if callable(filename):
        func = filename
        filename = None
        return decorator(func)

    return decorator

# ------------------ Функция-отчёт ------------------
@save_report  # можно также использовать @save_report("my_report.csv")
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца от переданной даты.
    Если дата не передана, используется текущая дата.
    :param transactions: DataFrame с транзакциями
    :param category: Название категории (например, 'Супермаркеты')
    :param date: Опциональная дата в формате 'DD-MM-YYYY'
    :return: DataFrame с отфильтрованными данными
    """
    logging.info(f"Формирование отчёта по категории: {category}")

    # Определяем дату отсчёта
    if date:
        end_date = datetime.strptime(date, "%Y.%m.%d")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    # Приводим колонку с датами к datetime
    transactions['Дата операции'] = pd.to_datetime(
        transactions['Дата операции'],
        errors='coerce',
        format='%Y.%m.%d %H:%M:%S'
    )

    # Фильтрация
    filtered = transactions[
        (transactions['Категория'] == category) &
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date)
        ]

    logging.info(f"Найдено {len(filtered)} транзакций по категории '{category}' за последние 3 месяца.")
    return filtered

# ------------------ Логирование ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S"
)


