import json

import pytest

from src.services import (analyze_cashback_categories, investment_bank, search_person_transfers,
                          search_phone_transactions, search_transactions)


def test_analyze_cashback_categories(valid_operations):
    result = analyze_cashback_categories(valid_operations, 2021, 12)
    expected_result = json.dumps(
        {"Ж/д билеты": 28.23, "Дом и ремонт": 25.0, "Супермаркеты": 12.65}, indent=4, ensure_ascii=False
    )
    assert result == expected_result


def test_less_3_categories_analyze_cashback_categories(less_3_categories):
    result = analyze_cashback_categories(less_3_categories, 2021, 12)
    expected_result = json.dumps({"Супермаркеты": 12.65, "Различные товары": 5.64}, indent=4, ensure_ascii=False)
    assert result == expected_result


def test_exactly_3_categories_analyze_cashback_categories(exactly_3_categories):
    result = analyze_cashback_categories(exactly_3_categories, 2021, 12)
    expected_result = json.dumps(
        {"Ж/д билеты": 28.23, "Супермаркеты": 12.65, "Каршеринг": 9.65}, indent=4, ensure_ascii=False
    )
    assert result == expected_result


def test_invalid_data_analyze_cashback_categories(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных."):
        analyze_cashback_categories(invalid_operations, 2021, 12)


def test_empty_result_analyze_cashback_categories(valid_operations):
    result = analyze_cashback_categories(valid_operations, 2025, 1)
    expected_result = json.dumps({}, indent=4, ensure_ascii=False)
    assert result == expected_result


def test_investment_bank(dict_transactions):
    result = investment_bank("2021-12", dict_transactions, 50)
    expected_result = 672.2
    assert result == expected_result
    assert isinstance(result, float)


@pytest.mark.parametrize("limit", [-100, -999, -99.2])
def test_invalid_limit_investment_bank(dict_transactions, limit):
    with pytest.raises(ValueError, match="limit должен быть положительным числом."):
        investment_bank("2021-12", dict_transactions, limit)


def test_invalid_transactions_investment_bank(invalid_operations):
    result = investment_bank("2021-12", invalid_operations, 50)
    expected_result = 0.0
    assert result == expected_result
    assert isinstance(result, float)


@pytest.mark.parametrize("month", ["2018-12", "2019-12", "2016-12"])
def test_wrong_date_investment_bank(dict_transactions, month):
    result = investment_bank(month, dict_transactions, 50)
    expected_result = 0.0
    assert result == expected_result
    assert isinstance(result, float)


def test_no_expenses_investment_bank(no_expenses):
    no_expenses.to_dict(orient="records")
    result = investment_bank("2021-12", no_expenses, 50)
    expected_result = 0.0
    assert result == expected_result
    assert isinstance(result, float)


def test_transaction_multiple_investment_bank(transaction_multiple):
    result = investment_bank("2021-12", transaction_multiple, 50)
    expected_result = 633.09
    assert result == expected_result
    assert isinstance(result, float)


def test_search_transactions(dict_transactions):
    result = search_transactions("колхоз", dict_transactions)
    expected_result = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Сумма платежа": -160.89,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 3.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 160.89,
        },
        {
            "Дата операции": "31.12.2021 16:42:04",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -64.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -64.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 1.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 64.0,
        },
        {
            "Дата операции": "31.12.2021 15:44:39",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -78.05,
            "Валюта операции": "RUB",
            "Сумма платежа": -78.05,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 1.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 78.05,
        },
        {
            "Дата операции": "28.12.2021 13:44:39",
            "Дата платежа": "28.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -381.48,
            "Валюта операции": "RUB",
            "Сумма платежа": -381.48,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 7.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 381.48,
        },
    ]
    expected_json = json.dumps(expected_result, indent=4, ensure_ascii=False)
    assert result == expected_json
    assert len(expected_json) == len(result)
    assert isinstance(result, str)


def test_empty_result_search_transactions(dict_transactions):
    result = search_transactions("Каршеринг", dict_transactions)
    expected_result = []
    expected_json = json.dumps(expected_result)
    assert result == expected_json
    assert len(expected_json) == len(result)
    assert isinstance(result, str)


def test_wrong_type_description_search_transactions(description_not_string):
    result = search_transactions("Такси", description_not_string)
    expected_result = []
    expected_json = json.dumps(expected_result)
    assert result == expected_json
    assert len(expected_json) == len(result)
    assert isinstance(result, str)


def test_no_description_search_transactions(no_description):
    result = search_transactions("Супермаркеты", no_description)
    expected_result = []
    expected_json = json.dumps(expected_result)
    assert result == expected_json
    assert len(expected_json) == len(result)
    assert isinstance(result, str)


def test_search_phone_transactions(transactions_with_phones):
    result = search_phone_transactions(transactions_with_phones)
    expected_result = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Сумма платежа": -160.89,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Пополнение +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 3.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 160.89,
        },
        {
            "Дата операции": "31.12.2021 00:12:53",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*5091",
            "Статус": "OK",
            "Сумма операции": -800.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -800.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": 5411.0,
            "Описание": "Пополнение +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 0.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 800.0,
        },
        {
            "Дата операции": "30.12.2021 17:50:17",
            "Дата платежа": "30.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 174000.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 174000.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Пополнения",
            "MCC": 5411.0,
            "Описание": "Пополнение +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 0.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 174000.0,
        },
        {
            "Дата операции": "29.12.2021 15:08:20",
            "Дата платежа": "29.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -383.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -383.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Дом и ремонт",
            "MCC": 5200.0,
            "Описание": "Пополнение +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 7.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 383.0,
        },
        {
            "Дата операции": "28.12.2021 13:44:39",
            "Дата платежа": "28.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -381.48,
            "Валюта операции": "RUB",
            "Сумма платежа": -381.48,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Пополнение +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 7.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 381.48,
        },
        {
            "Дата операции": "27.12.2021 15:56:23",
            "Дата платежа": "27.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -35.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -35.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Связь",
            "MCC": 7379.0,
            "Описание": "Пополнение +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 0.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 35.0,
        },
    ]
    expected_json = json.dumps(expected_result, indent=4, ensure_ascii=False)
    assert result == expected_json


def test_empty_result_search_phone_transactions(dict_transactions):
    result = search_phone_transactions(dict_transactions)
    expected_result = []
    expected_json = json.dumps(expected_result, indent=4, ensure_ascii=False)
    assert result == expected_json


def test_search_person_transfers(dict_transactions):
    result = search_person_transfers(dict_transactions)
    expected_result = [
        {
            "Дата операции": "31.12.2021 00:12:53",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*5091",
            "Статус": "OK",
            "Сумма операции": -800.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -800.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": 5411.0,
            "Описание": "Константин Л.",
            "Бонусы (включая кэшбэк)": 0.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 800.0,
        },
        {
            "Дата операции": "30.12.2021 22:22:03",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -20000.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -20000.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": 5411.0,
            "Описание": "Константин Л.",
            "Бонусы (включая кэшбэк)": 0.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 20000.0,
        },
    ]
    expected_json = json.dumps(expected_result, indent=4, ensure_ascii=False)
    assert result == expected_json


def test_empty_result_search_person_transfers(no_description):
    result = search_person_transfers(no_description)
    expected_result = []
    expected_json = json.dumps(expected_result, indent=4, ensure_ascii=False)
    assert result == expected_json
