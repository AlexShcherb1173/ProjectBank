# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
import pandas as pd
from reports import spending_by_category
#
# # Загружаем тестовый Excel
df = pd.read_excel(r"C:\Users\alex_\PycharmProjects\ProjectBank\data\operations.xlsx")
# print(df.head())
# Вызываем отчёт (без имени файла — создастся автоматически)
report = spending_by_category(df, "Супермаркеты")

# Если хотите своё имя файла:
# from reports import save_report
# @save_report("my_custom_report.csv")
# def spending_by_category(...):
#     ...
#def sample_transactions():
    #"""Тестовый датафрейм с 3 строками, одна из которых старше 3 месяцев."""
# df = {
#         "Дата операции": [
#             "2025.07.31 16:44:00",
#             "2025.07.31 16:42:04",
#             "2021.09.15 10:10:10"  # старше 3 месяцев от 31.12.2021
#         ],
#         "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
#         "Сумма операции": [-160.89, -64.00, -500.00]
#         }
# data = pd.DataFrame(df)
#
# filt = spending_by_category(data, category="Супермаркеты")
# print(filt)