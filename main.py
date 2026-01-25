import json
from pathlib import Path

import pandas as pd

from src.reports import spending_by_category
from src.services import simple_search
from src.utils import load_transactions
from src.views import generate_report

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Загружаем Excel
excel_path = DATA_DIR / "operations.xlsx"
df = pd.read_excel(excel_path)

# Отчёт по категории
report = spending_by_category(df, "Супермаркеты")

# Альтернативная загрузка через utils
df = load_transactions("data/operations.xlsx")
transactions = df.to_dict(orient="records")

query = "Колхоз"
json_result = simple_search(query, transactions)
result = json.loads(json_result)

print(result)


if __name__ == "__main__":
    print(generate_report("2021-12-31 16:00:00"))
