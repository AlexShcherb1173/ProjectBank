# 📊 Финансовый отчет — Python проект

## 📌 Описание
Проект предназначен для обработки финансовых транзакций, генерации отчетов, поиска по транзакциям и получения котировок валют и акций.  
Используются:
- **pandas** — обработка транзакций
- **requests** — API валют и акций
- **logging** — отладка и логирование
- **json** — работа с настройками и ответами функций

---

## 📂 Структура проекта

### **views.py** - главная функция:  
##### def generate_report(date_str: str, df) -> str  
Генерация итогового отчета за выбранный период.
### utils.py — вспомогательные функции  
```python
| Функция                                                                                 | Описание                                                |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `get_greeting(dt: datetime) -> str`                                                     | Приветствие пользователя в зависимости от времени суток |
| `filter_transactions_by_date(df: pd.DataFrame, start: datetime, end: datetime) -> `     | Фильтрация транзакций по диапазону дат                  |
| `pd.DataFrame`                                                                          |                                                         |
| `aggregate_cards(df: pd.DataFrame)`                                                     | Суммирование трат по картам с расчетом кешбэка          |
| `get_top_transactions(df: pd.DataFrame, top_n=5)`                                       | Отбор топ-транзакций по убыванию суммы                  |
| `get_currency_rates(currencies)`                                                        | Получение курса валют                                   |
| `get_stock_prices(stocks)`                                                              | Получение котировок акций                               |
| `load_user_settings(path="user_settings.json")`                                         | Загрузка пользовательских настроек из файла             |
| `load_transactions(file_path: str) -> pd.DataFrame:`                                    | Создает DataFrame из xlsx файла                         |
```
#### user_settings.json  
##### Файл с пользовательскими настройками:  
###### json   
_{
    "currencies": ["USD", "EUR"],   
    "stocks": ["AAPL", "TSLA"]
}_  

### services.py — сервисы проекта  

##### Простой поиск по транзакциям:  
##### def simple_search(query: str, transactions: List[Dict]) -> str  
🔹 Логирует процесс поиска  
🔹 Если запрос пустой — возвращает пустой список  
🔹 Поиск по "Описание" и "Категория" без учета регистра  
🔹 Возвращает результат в JSON с красивым форматированием (indent=4, ensure_ascii=False)  

### reports.py — модуль отчетов  
##### Декоратор  
##### def save_report(filename: Optional[str] = None)  
Сохраняет результат функции-отчета в CSV.  
Если имя файла не задано — генерируется автоматически по текущей дате/времени.  

##### Функция отчета  
##### @save_report  
##### def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame  
📌 Возвращает траты по заданной категории за последние 3 месяца.  
📌 Логирует:  
_категорию отчета  
количество найденных транзакций  
путь к сохраненному файлу_  

## Архитектура проекта

    A[views.py] -->|генерация отчета| B[utils.py]
    A --> C[services.py]
    A --> D[reports.py]
    B -->|получение данных| E[user_settings.json]
    B -->|API запросы| F[(Валюты и акции API)]
    D -->|CSV отчеты| G[(report_*.csv)]

### Примеры JSON-ответов  
#### Пример ответа simple_search:  

_[  
    {  
        "Дата": "2023-09-05",  
        "Описание": "Супермаркет",  
        "Категория": "Продукты",  
        "Сумма": 4500  
    },  
    {  
        "Дата": "2023-09-06",  
        "Описание": "АЗС Shell",  
        "Категория": "Топливо",  
        "Сумма": 3200  
    }  
]_  

#### Пример ответа get_currency_rates:  

_{  
    "USD": 95.42,  
    "EUR": 102.15  
}_   

## 🛠 Установка и запуск  

__git clone <репозиторий>  
cd <папка_проекта>  
pip install -r requirements.txt__   

## ✅ Пример использования  
__from utils import get_greeting, get_currency_rates  
from datetime import datetime__  

__print(get_greeting(datetime.now()))  
print(get_currency_rates(["USD", "EUR"]))__  

## 📜 Лицензия  
#### __MIT License__  

---