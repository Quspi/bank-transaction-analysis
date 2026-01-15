import json
import os

from src.reports import save_report, spending_by_category, spending_by_weekday, spending_by_workday
from src.services import (analyze_cashback_categories, investment_bank, search_person_transfers,
                          search_phone_transactions, search_transactions)
from src.utils import load_xlsx_transactions
from src.views import get_events_page_data, get_main_page_data

BASE_DIR = os.path.dirname(__file__)
TRANSACTIONS_PATH = os.path.join(BASE_DIR, "data", "operations.xlsx")

if __name__ == "__main__":
    # Веб-страницы:
    result_events_page = get_events_page_data("2021-12-23 02:34:12")
    print("События:")
    print(result_events_page)

    result_main_page = get_main_page_data("2020-10-26 16:51:06")
    print("Главная:")
    print(result_main_page)

    transactions_df = load_xlsx_transactions(TRANSACTIONS_PATH)
    transactions_list = transactions_df.to_dict(orient="records")

    # Сервисы:
    result_analyze_cashback = analyze_cashback_categories(transactions_list, 2020, 11)
    print("Выгодные категории повышенного кэшбэка:")
    print(result_analyze_cashback)

    result_investment_bank = investment_bank("2021-11", transactions_list, 50)
    print("Инвесткопилка:")
    print(result_investment_bank)

    print("Простой поиск:")
    search_string = input("Поиск по описанию: ")
    search_transactions_json = search_transactions(search_string, transactions_list)
    result_search_transactions = json.loads(search_transactions_json)
    print(f"Найдено {len(result_search_transactions)} транзакций")
    if result_search_transactions:
        print("Пример вывода:", json.dumps(result_search_transactions[:5], indent=4, ensure_ascii=False))
    else:
        print(f"Не найдено операций по запросу {search_string}")

    search_phone_transactions_json = search_phone_transactions(transactions_list)
    result_search_phone_transactions = json.loads(search_phone_transactions_json)
    print("Поиск по телефонным номерам:")
    print(f"Найдено {len(result_search_phone_transactions)} транзакций")
    print("Пример вывода:", json.dumps(result_search_phone_transactions[:5], indent=4, ensure_ascii=False))

    search_person_transfers_json = search_person_transfers(transactions_list)
    result_search_person_transfers = json.loads(search_person_transfers_json)
    print("Поиск переводов физическим лицам:")
    print(f"Найдено {len(result_search_person_transfers)} транзакций")
    print("Пример вывода:", json.dumps(result_search_person_transfers[:5], indent=4, ensure_ascii=False))

    # Отчеты:
    decorated_spending_by_category = save_report()(spending_by_category)
    result_spending_by_category = decorated_spending_by_category(transactions_df, "Транспорт", "01-06-2020")
    print("Траты по категории:")
    print(result_spending_by_category)

    decorated_spending_by_weekday = save_report("test_file_name_1")(spending_by_weekday)
    result_spending_by_weekday = decorated_spending_by_weekday(transactions_df, "08-05-2019")
    print("Траты по дням недели:")
    print(result_spending_by_weekday)

    decorated_spending_by_workday = save_report("test_file_name_2")(spending_by_workday)
    result_spending_by_workday = decorated_spending_by_workday(transactions_df, "20-05-2018")
    print("Траты в рабочий/выходной день:")
    print(result_spending_by_workday)
