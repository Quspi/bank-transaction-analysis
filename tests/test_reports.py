import os

import pandas as pd
import pytest

from src.reports import save_report, spending_by_category, spending_by_weekday


@save_report()
def df_func():
    return pd.DataFrame([{"a": 1}])


def test_save_report_no_filename():
    result = df_func()
    assert os.path.exists("data/df_func_report.json")
    os.remove("data/df_func_report.json")


@save_report("test_name")
def func_with_df():
    return pd.DataFrame([{"b": 2}])


def test_save_report_with_filename():
    result = func_with_df()
    assert os.path.exists("data/test_name_report.json")
    os.remove("data/test_name_report.json")


@save_report()
def func_no_df():
    return "not df"


def test_save_report_no_df():
    result = func_no_df()
    assert not os.path.exists("data/func_no_df_report.json")
    assert isinstance(result, str)


def test_spending_by_category(valid_operations):
    result = spending_by_category(valid_operations, "Супермаркеты", "31-12-2021")
    result_dict = result.to_dict(orient="records")
    expected_result = [{"Период": "2021-12", "Сумма": 843.7}]
    assert result_dict == expected_result


def test_invalid_data_spending_by_category(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных."):
        spending_by_category(invalid_operations, "Супермаркеты")


def test_no_data_spending_by_category(valid_operations):
    result = spending_by_category(valid_operations, "Несуществующая категория", "31-12-2021")
    result_dict = result.to_dict(orient="records")
    expected_result = []
    assert result.empty
    assert result_dict == expected_result


def test_invalid_date_spending_by_category(valid_operations):
    with pytest.raises(ValueError, match="Некорректный формат даты"):
        spending_by_category(valid_operations, "Супермаркеты", "32-21-2021")


def test_spending_by_weekday(valid_operations):
    result = spending_by_weekday(valid_operations, "31-12-2021")
    result_dict = result.to_dict(orient="records")
    expected_result = [
        {"День недели": "Понедельник", "Сумма": 57.88},
        {"День недели": "Вторник", "Сумма": 485.08},
        {"День недели": "Среда", "Сумма": 678.58},
        {"День недели": "Четверг", "Сумма": 5089.35},
        {"День недели": "Воскресенье", "Сумма": 415.32},
    ]
    assert result_dict == expected_result


def test_invalid_data_spending_by_weekday(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных."):
        spending_by_weekday(invalid_operations)


def test_invalid_date_spending_by_weekday(valid_operations):
    with pytest.raises(ValueError, match="Некорректный формат даты"):
        spending_by_weekday(valid_operations, "32-21.2021")


def test_empty_result_spending_by_weekday(valid_operations):
    result = spending_by_weekday(valid_operations)
    result_dict = result.to_dict(orient="records")
    expected_result = []
    assert result_dict == expected_result
