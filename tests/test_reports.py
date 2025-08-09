# Что тестируем
    # Фильтрация — проверяем, что данные за пределами последних 3 месяцев не попадают в отчёт.
    # Декоратор с параметром — проверяем, что файл создаётся с заданным именем и содержит все данные.
    # Декоратор без параметра — проверяем, что файл создаётся с автоименем report_YYYYMMDD_HHMMSS.csv.

    # Создали класс FixedDateTime, где now() всегда возвращает 2021 - 12 - 31.
    #  В тесте test_spending_by_category_filtering подменяем datetime внутри модуля reports с помощью:
    #
    # monkeypatch.setattr("reports.datetime", FixedDateTime)
    # Tесты не зависят от реальной даты и всегда проверяют период с октября по декабрь 2021 года.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytest
from src.reports import spending_by_category, save_report


@pytest.fixture
def sample_transactions():
    """Тестовый датафрейм с 3 строками, одна из которых старше 3 месяцев."""
    data = {
        "Дата операции": [
            "2025.07.30 16:44:00",
            "2025.07.30 16:42:04",
            "2021.09.15 10:10:10"  # старше 3 месяцев от 31.12.2021
        ],
        "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
        "Сумма операции": [-160.89, -64.00, -500.00]
    }
    return pd.DataFrame(data)


# ------------------ Мокаем datetime.now ------------------
class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2025,7,30)  # фиксированная дата для тестов


def test_spending_by_category_filtering(sample_transactions, monkeypatch):
    # Мокаем datetime в модуле reports
    monkeypatch.setattr("reports.datetime", FixedDateTime)

    result = spending_by_category(
        sample_transactions,
        category="Супермаркеты"
    )

    # Проверка: строки только в пределах последних 3 месяцев
    assert all(result["Дата операции"] >= pd.Timestamp("2021.10.01"))
    assert all(result["Дата операции"] <= pd.Timestamp("2025.07.31"))
    # Проверка количества строк (третья строка должна быть отфильтрована)
    assert len(result) == 2


def test_save_report_with_filename(sample_transactions):
    file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'folder_test')), "report_1.csv")
    # tmp_path = Path('test_folder')
    # tmp_path.mkdir(exist_ok=True, parents=True)
    # file_path = tmp_path/"custom_report.csv"

    @save_report(str(file_path))
    def dummy_report(df):
        return df

    dummy_report(sample_transactions)

    assert os.path.exists(file_path)
    saved_df = pd.read_csv(file_path)
    assert len(saved_df) == len(sample_transactions)


def test_save_report_default_filename(sample_transactions, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    @save_report
    def dummy_report(df):
        return df

    dummy_report(sample_transactions)

    #files = list(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'report'))).glob("report_*.csv"))
    report_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'folder_test')))
    files = list(report_dir.glob("report_*.csv"))
    assert len(files) == 1
    saved_df = pd.read_csv(files[0])
    assert len(saved_df) == len(sample_transactions)

