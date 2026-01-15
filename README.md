# Приложение для анализа банковских операций

Проект предоставляет инструменты для анализа финансовых операций из Excel-файлов. Включает генерацию JSON-данных для веб-страниц, формирование Excel-отчетов, поиск транзакций, расчет статистики и получение информации о курсах валют и акций. Реализован с использованием модульной архитектуры, покрыт тестами и включает логирование.

![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Tests](https://img.shields.io/badge/tests-100%25_passing-success)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

## Оглавление

1. [Технологии](#технологии)
2. [Функциональность](#функциональность)
3. [Поддерживаемые форматы данных](#поддерживаемые-форматы-данных)
4. [Логирование](#логирование)
5. [Установка](#установка)
6. [Использование модулей](#использование-модулей)
7. [Тестирование](#тестирование)
8. [Лицензия](#лицензия)
9. [Автор](#автор)

## Технологии
- Python 3.12
- Pandas (анализ данных)
- JSON (сериализация)
- Requests (API запросы)
- Pytest (тестирование)
- Logging (логирование)

## Функциональность

### Реализовано
- Отчеты: анализ расходов по категориям, дням недели и типам дней
- Сервисы: поиск транзакций, анализ кэшбэка, расчёт инвестиций
- Утилиты: обработка транзакций, статистика карт, курсы валют и акций
- Представления: формирование JSON-ответов для веб-интерфейса

## Поддерживаемые форматы данных
- **Excel**: .xlsx, .xls

## Логирование

- Логирование модульное, логи записываются в папку logs/

## Установка
```
# Клонирование репозитория
git clone https://github.com/Quspi/bank-transaction-analysis.git

# Установка зависимостей
poetry install

# Настройка переменных окружения для работы с API
Создайте файл .env в корне проекта по шаблону env.example
```

## Использование модулей
<details>
<summary>Отчеты (reports.py)</summary>

```python
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday, save_report

spending_by_category(transactions, "Супермаркеты", "31-12-2021")
# Возвращает DataFrame:
#   Период     Сумма
#   2021-12    843.7


spending_by_weekday(transactions, "31-12-2021")
# Возвращает DataFrame:
#   День недели     Сумма
#   Понедельник    512.45
#   Вторник        423.10
# ... (другие дни недели)



spending_by_workday(transactions, "31-12-2021")
# Возвращает DataFrame:
#   Тип дня     Сумма
#   Рабочий    467.25
#   Выходной   689.30


@save_report("spending_report")
def generate_report():
    return spending_by_category(transactions, "Супермаркеты")    
# Результат сохраняется в data/spending_report_report.json
```
</details>

<details>
<summary>Сервисы (services.py)</summary>

```python
from src.services import (analyze_cashback_categories, investment_bank, 
                         search_transactions, search_phone_transactions, 
                         search_person_transfers)

analyze_cashback_categories(transactions, 2021, 12)
# Возвращает JSON: {"Супермаркеты": 843.7, "Рестораны": 512.3, "Транспорт": 410.5}

investment_bank("2021-12", transactions, 100)
# Возвращает float: 47.0

search_transactions("Пятёрочка", transactions)
# Возвращает JSON-массив транзакций с "Пятёрочка" в описании

search_phone_transactions(transactions)
# Возвращает JSON-массив транзакций с номерами телефонов

search_person_transfers(transactions)
# Возвращает JSON-массив переводов физическим лицам
```
</details>

<details>
<summary>Утилиты (utils.py)</summary>

```python
from src.utils import (get_greetings, load_user_settings, get_currencies, get_stocks,
                      load_xlsx_transactions, calculate_card_statistics, get_top_transactions,
                      filter_transactions_by_period, get_exchange_rates, get_stock_prices,
                      collect_data_for_main_page, get_expenses_report, get_income_report,
                      collect_data_for_events_page)

# Примеры использования utils.py
get_greetings()
# Возвращает строку: "Добрый день" (в зависимости от времени суток)

load_user_settings("user_settings.json")
# Возвращает словарь: {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}

get_currencies(user_settings)
# Возвращает список: ["USD", "EUR"]

get_stocks(user_settings)
# Возвращает список: ["AAPL"]

load_xlsx_transactions("data/operations.xlsx")
# Возвращает DataFrame с транзакциями

calculate_card_statistics(transactions_df)
# Возвращает список: [{"last_digits": "7197", "total_spent": 15600.5, "cashback": 156.01}]

get_top_transactions(transactions_df)
# Возвращает список топ-5 транзакций: [{"date": "31.12.2021", "amount": -160.89, ...}]

filter_transactions_by_period(transactions_df, "2021-12-31 16:44:00", "M")
# Возвращает DataFrame транзакций за декабрь 2021

get_exchange_rates(["USD", "EUR"])
# Возвращает список: [{"currency": "USD", "rate": 75.45}, {"currency": "EUR", "rate": 90.12}]

get_stock_prices(["AAPL", "TSLA"])
# Возвращает список: [{"stock": "AAPL", "currency": "USD", "price": 175.34}, ...]

collect_data_for_main_page("2021-12-31 16:44:00")
# Возвращает словарь с данными для главной страницы

get_expenses_report(transactions_df)
# Возвращает словарь с отчетом по расходам

get_income_report(transactions_df)
# Возвращает словарь с отчетом по доходам

collect_data_for_events_page("2021-12-31 16:44:00", "M")
# Возвращает словарь с данными для страницы событий
```
</details>

<details>
<summary>Представления (views.py)</summary>

```python
from src.views import get_main_page_data, get_events_page_data

# Примеры использования views.py
get_main_page_data("2021-12-31 16:44:00")
# Возвращает JSON строку с данными для главной страницы

get_events_page_data("2021-12-31 16:44:00", "M")
# Возвращает JSON строку с данными для страницы событий за месяц

get_events_page_data("2021-12-31 16:44:00", "W")
# Возвращает JSON строку с данными для страницы событий за неделю
```
</details>

<details>
<summary>Демонстрация (main.py)</summary>

Файл `main.py` демонстрирует работу всех функциональностей проекта:

```bash
# Запуск демонстрации
python main.py
```

Что выполняется при запуске:
- Генерация JSON-данных для веб-страниц "Главная" и "События"
- Анализ выгодных категорий для кэшбэка
- Расчёт суммы для инвестиционного пополнения
- Поиск транзакций по различным критериям
- Создание отчётов с автоматическим сохранением в JSON-файлы

Результаты:
- JSON-ответы выводятся в консоль
- Отчёты сохраняются в папку data/
- Примеры транзакций выводятся в удобочитаемом формате

</details>

## Тестирование

Проект покрыт юнит-тестами Pytest. Для их запуска выполните команды:
```
# Запуск всех тестов
pytest

# Запуск с отчетом о покрытии в консоли
pytest --cov=src

# Генерация HTML отчета о покрытии (будет создана папка htmlcov/)
pytest --cov=src --cov-report=html
```

## Лицензия
Этот проект распространяется под лицензией MIT.

## Автор
**Oleg Tamanov**

Email: olegtamanov@gmail.com