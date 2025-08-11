import json

import pandas as pd

from src.reports import spending_by_category
from src.services import simple_search
from src.utils import load_transactions
from src.views import generate_report

#
# # Загружаем тестовый Excel
df = pd.read_excel(r"C:\Users\alex_\PycharmProjects\ProjectBank\data\operations.xlsx")
# # print(df.head())
# # Вызываем отчёт (без имени файла — создастся автоматически)
report = spending_by_category(df, "Супермаркеты")


df = load_transactions("data/operations.xlsx")
transactions = df.to_dict(orient="records")
query = "Колхоз"
#
json_result = simple_search(query, transactions)
result = json.loads(json_result)
print(result)


if __name__ == "__main__":
    print(generate_report("2021-12-31 16:00:00"))
