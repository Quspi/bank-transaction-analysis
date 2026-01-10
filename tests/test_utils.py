import json
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils import (calculate_card_statistics, get_currencies, get_greetings, get_stocks, load_user_settings,
                       load_xlsx_transactions)


@pytest.mark.parametrize(
    "hour, expected_result",
    [
        (5, "Доброе утро"),
        (10, "Доброе утро"),
        (11, "Добрый день"),
        (15, "Добрый день"),
        (16, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (4, "Доброй ночи"),
    ],
)
def test_get_greetings(hour, expected_result):
    with freeze_time(f"2026-01-01 {hour}:00:00"):
        result = get_greetings()
        assert result == expected_result


@patch("builtins.open")
@patch("json.load")
def test_load_user_settings(mocked_load, mocked_open, valid_settings):
    mocked_load.return_value = valid_settings
    result = load_user_settings("test_path")
    assert result == valid_settings
    mocked_open.assert_called_once_with("test_path", "r", encoding="utf-8")


@patch("builtins.open", side_effect=FileNotFoundError)
def test_invalid_path_load_user_settings(mocked_open):
    with pytest.raises(ValueError, match="Файл не найден или удален."):
        load_user_settings("invalid_path")
    mocked_open.assert_called_once_with("invalid_path", "r", encoding="utf-8")


def test_invalid_json_load_user_settings():
    with patch("builtins.open", mock_open(read_data="{}")) as mocked_open:
        with patch("json.load", side_effect=json.JSONDecodeError("error", "doc", 0)) as mocked_load:
            with pytest.raises(ValueError, match="Файл повреждён или пуст."):
                load_user_settings("test_path")
            mocked_open.assert_called_once_with("test_path", "r", encoding="utf-8")
            mocked_load.assert_called_once()


def test_invalid_data_load_user_settings():
    invalid_data = {"key": []}
    with patch("builtins.open", mock_open()) as mocked_open:
        with patch("json.load", return_value=invalid_data) as mocked_load:
            with pytest.raises(ValueError, match="Ошибка в структуре данных."):
                load_user_settings("invalid.json")
                mocked_open.assert_called_once_with("invalid.json", "r", encoding="utf-8")
                mocked_load.assert_called_once()


def test_get_currencies(valid_settings):
    result = get_currencies(valid_settings)
    expected_result = ["USD", "EUR"]
    assert result == expected_result


def test_invalid_data_get_currencies():
    invalid_data = {"key": []}
    with pytest.raises(KeyError):
        get_currencies(invalid_data)


def test_get_stocks(valid_settings):
    result = get_stocks(valid_settings)
    expected_result = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    assert result == expected_result


def test_invalid_data_get_stocks():
    invalid_data = {"key": []}
    with pytest.raises(KeyError):
        get_stocks(invalid_data)


@patch("src.utils.pd.read_excel")
def test_load_xlsx_transactions(mocked_read_xlsx):
    df = pd.DataFrame({"col": [1]})
    mocked_read_xlsx.return_value = df
    result = load_xlsx_transactions("test.xlsx")
    pd.testing.assert_frame_equal(result, df)


@patch("src.utils.pd.read_excel", side_effect=pd.errors.EmptyDataError)
def test_empty_df_load_xlsx_transactions(mocked_read_xlsx):
    with pytest.raises(ValueError, match="Файл не содержит данные."):
        load_xlsx_transactions("empty.xlsx")
        mocked_read_xlsx.assert_called_once_with("empty.xlsx")


@patch("src.utils.pd.read_excel", side_effect=FileNotFoundError)
def test_invalid_path_load_xlsx_transactions(mocked_read_xlsx):
    with pytest.raises(ValueError, match="Файл не найден или удален."):
        load_xlsx_transactions("not_found.xlsx")
        mocked_read_xlsx.assert_called_once_with("not_found.xlsx")


@patch("src.utils.pd.read_excel", side_effect=KeyError)
def test_invalid_sheet_name_load_xlsx_transactions(mocked_read_xlsx):
    with pytest.raises(KeyError):
        load_xlsx_transactions("file.xlsx", sheet_name="invalid")
        mocked_read_xlsx.assert_called_once_with("file.xlsx", sheet_name="invalid")


def test_calculate_card_statistics(valid_operations):
    result = calculate_card_statistics(valid_operations)
    expected_result = [
        {"last_digits": "4556", "total_spent": 2822.8, "cashback": 28.23},
        {"last_digits": "5091", "total_spent": 2497.28, "cashback": 24.97},
        {"last_digits": "7197", "total_spent": 24257.72, "cashback": 242.58},
    ]
    assert result == expected_result


def test_invalid_data_calculate_card_statistics(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных."):
        calculate_card_statistics(invalid_operations)


def test_empty_result_calculate_card_statistics(invalid_status_operations):
    result = calculate_card_statistics(invalid_status_operations)
    expected_result = []
    assert result == expected_result
