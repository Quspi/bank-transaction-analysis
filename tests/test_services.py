import json

import pytest

from src.services import analyze_cashback_categories, investment_bank


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
    result = investment_bank("2021-12", no_expenses, 50)
    expected_result = 0.0
    assert result == expected_result
    assert isinstance(result, float)


def test_transaction_multiple_investment_bank(transaction_multiple):
    result = investment_bank("2021-12", transaction_multiple, 50)
    expected_result = 633.09
    assert result == expected_result
    assert isinstance(result, float)
