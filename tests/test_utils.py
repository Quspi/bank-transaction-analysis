import json
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest
import requests
from freezegun import freeze_time

from src.utils import (calculate_card_statistics, collect_data_for_events_page, collect_data_for_main_page,
                       filter_transactions_by_period, get_currencies, get_exchange_rates, get_expenses_report,
                       get_greetings, get_income_report, get_stock_prices, get_stocks, get_top_transactions,
                       load_user_settings, load_xlsx_transactions)


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


def test_get_top_transactions(valid_operations):
    result = get_top_transactions(valid_operations)
    expected_result = [
        {
            "date": "30.12.2021",
            "amount": 174000.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк",
        },
        {"date": "30.12.2021", "amount": -20000.0, "category": "Переводы", "description": "Константин Л."},
        {
            "date": "30.12.2021",
            "amount": 5046.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк",
        },
        {"date": "28.12.2021", "amount": -1840.0, "category": "Дом и ремонт", "description": "Галамарт"},
        {"date": "29.12.2021", "amount": -1411.4, "category": "Ж/д билеты", "description": "РЖД"},
    ]
    assert result == expected_result


def test_invalid_data_get_top_transactions(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных."):
        get_top_transactions(invalid_operations)


def test_empty_result_get_top_transactions(invalid_status_operations):
    result = get_top_transactions(invalid_status_operations)
    expected_result = []
    assert result == expected_result


@pytest.mark.parametrize(
    "period, expected_start",
    [
        ("M", "2021-12-01"),
        ("W", "2021-12-27"),
        ("Y", "2021-01-01"),
        ("ALL", None),
    ],
)
def test_filter_transactions_by_period(valid_operations, period, expected_start):
    end_date = "2021-12-31 00:00:00"
    result = filter_transactions_by_period(valid_operations, end_date, period)
    if expected_start:
        assert result["Дата операции"].min() >= pd.Timestamp(expected_start)
    assert result["Дата операции"].max() <= pd.Timestamp(end_date)


@pytest.mark.parametrize(
    "date, period, match",
    [
        ("31-12-2021", "M", "Некорректный формат даты"),
        ("2021-12-31 00:00:00", "invalid", "Некорректное значение period"),
        ("2025-12-31 00:00:00", "Y", "Транзакций за указанный период не найдено."),
    ],
)
def test_invalid_period_transactions_by_period(valid_operations, date, period, match):
    with pytest.raises(ValueError, match=match):
        filter_transactions_by_period(valid_operations, date, period)


def test_invalid_data_transactions_by_period(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных."):
        filter_transactions_by_period(invalid_operations, "2021-12-31 00:00:00", "W")


@patch("requests.get")
def test_get_exchange_rates(mock_get):
    mock_get.return_value.json.return_value = {"Valute": {"USD": {"CharCode": "USD", "Value": 75.5}}}
    result = get_exchange_rates(["USD"])
    assert result == [{"currency": "USD", "rate": 75.5}]


def test_empty_result_get_exchange_rates():
    result = get_exchange_rates([])
    expected_result = []
    assert result == expected_result


@patch("requests.get")
def test_http_error_get_exchange_rates(mock_get):
    http_error = requests.exceptions.HTTPError()
    http_error.response = Mock(status_code=404)
    mock_get.side_effect = http_error
    with pytest.raises(ConnectionError, match="HTTP ошибка, код ошибки:"):
        get_exchange_rates(["USD"])


@patch("requests.get")
def test_connection_error_get_exchange_rates(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError
    with pytest.raises(ConnectionError, match="Ошибка соединения:"):
        get_exchange_rates(["USD"])


@patch("requests.get")
def test_timeout_error_get_exchange_rates(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout
    with pytest.raises(TimeoutError, match="Таймаут запроса:"):
        get_exchange_rates(["USD"])


@patch("requests.get")
def test_invalid_response_get_exchange_rates(mock_get):
    mock_get.return_value.json.return_value = {"key": {"USD": {"CharCode": "USD", "Value": 75.5}}}
    result = get_exchange_rates(["USD"])
    expected_result = []
    assert result == expected_result


@patch("requests.get")
def test_invalid_currency_get_exchange_rates(mock_get):
    mock_get.return_value.json.return_value = {"Valute": {"USD": {"CharCode": "USD", "Value": 75.5}}}
    result = get_exchange_rates(["currency"])
    expected_result = []
    assert result == expected_result


@patch("time.sleep")
@patch("requests.get")
@patch("os.getenv")
def test_get_stock_prices(mock_getenv, mock_get, mock_sleep):
    mock_get.return_value.json.return_value = {"Global Quote": {"01. symbol": "AAPL", "05. price": "150.0"}}
    mock_sleep.return_value = None
    mock_getenv.return_value = "api_key"
    result = get_stock_prices(["AAPL"])
    expected_result = [{"stock": "AAPL", "currency": "USD", "price": 150.0}]
    assert result == expected_result


def test_empty_result_get_stock_prices():
    result = get_stock_prices([])
    expected_result = []
    assert result == expected_result


@patch("time.sleep")
@patch("requests.get")
@patch("os.getenv")
def test_http_error_get_stock_prices(mock_getenv, mock_get, mock_sleep):
    http_error = requests.exceptions.HTTPError()
    http_error.response = Mock(status_code=404)
    mock_get.side_effect = http_error
    mock_getenv.return_value = "api_key"
    mock_sleep.return_value = None

    result = get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    expected_result = []
    assert result == expected_result
    assert mock_get.call_count == 5


@patch("time.sleep")
@patch("requests.get")
@patch("os.getenv")
def test_connection_error_get_stock_prices(mock_getenv, mock_get, mock_sleep):
    mock_get.side_effect = requests.exceptions.ConnectionError
    mock_getenv.return_value = "api_key"
    mock_sleep.return_value = None

    result = get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    expected_result = []
    assert result == expected_result
    assert mock_get.call_count == 5


@patch("time.sleep")
@patch("requests.get")
@patch("os.getenv")
def test_timeout_error_get_stock_prices(mock_getenv, mock_get, mock_sleep):
    mock_get.side_effect = requests.exceptions.Timeout
    mock_getenv.return_value = "api_key"
    mock_sleep.return_value = None

    result = get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    expected_result = []
    assert result == expected_result
    assert mock_get.call_count == 5


@patch("time.sleep")
@patch("requests.get")
@patch("os.getenv")
def test_invalid_response_get_stock_prices(mock_getenv, mock_get, mock_sleep):
    mock_getenv.return_value = "api_key"
    mock_sleep.return_value = None
    mock_get.return_value.json.return_value = {"invalid key": {"01. symbol": "AAPL", "05. price": "150.0"}}
    result = get_stock_prices(["AAPL"])
    expected_result = []
    assert result == expected_result
    mock_get.assert_called_once()


@patch("time.sleep")
@patch("requests.get")
@patch("os.getenv")
def test_key_error_get_stock_prices(mock_getenv, mock_get, mock_sleep):
    mock_getenv.return_value = "api_key"
    mock_sleep.return_value = None
    mock_get.return_value.json.return_value = {"Global Quote": {"invalid_key_1": "AAPL", "invalid_key_2": "150.0"}}
    with pytest.raises(KeyError):
        get_stock_prices(["AAPL"])


@patch("src.utils.get_greetings")
@patch("src.utils.load_xlsx_transactions")
@patch("src.utils.filter_transactions_by_period")
@patch("src.utils.calculate_card_statistics")
@patch("src.utils.get_top_transactions")
@patch("src.utils.load_user_settings")
@patch("src.utils.get_currencies")
@patch("src.utils.get_stocks")
@patch("src.utils.get_exchange_rates")
@patch("src.utils.get_stock_prices")
def test_collect_data_for_main_page(
    mock_stock_prices,
    mock_exchange_rates,
    mock_stocks,
    mock_currencies,
    mock_user_settings,
    mock_top_transactions,
    mock_card_statistics,
    mock_transactions_by_period,
    mock_xlsx_transactions,
    mock_get_greetings,
):
    mock_get_greetings.return_value = "Добрый день"
    mock_stock_prices.return_value = [{"stock": "AAPL", "currency": "USD", "price": 150.0}]
    mock_exchange_rates.return_value = [{"currency": "USD", "rate": 75.5}]
    mock_stocks.return_value = ["AAPL"]
    mock_currencies.return_value = ["USD"]
    mock_user_settings.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    mock_top_transactions.return_value = []
    mock_card_statistics.return_value = [
        {"last_digits": "4556", "total_spent": 2822.8, "cashback": 28.23},
        {"last_digits": "5091", "total_spent": 2497.28, "cashback": 24.97},
        {"last_digits": "7197", "total_spent": 24257.72, "cashback": 242.58},
    ]
    mock_transactions_by_period.return_value = pd.DataFrame()
    mock_xlsx_transactions.return_value = pd.DataFrame()

    result = collect_data_for_main_page("2021-12-23 02:34:12")
    expected_result = {
        "greeting": "Добрый день",
        "cards": [
            {"last_digits": "4556", "total_spent": 2822.8, "cashback": 28.23},
            {"last_digits": "5091", "total_spent": 2497.28, "cashback": 24.97},
            {"last_digits": "7197", "total_spent": 24257.72, "cashback": 242.58},
        ],
        "top_transactions": [],
        "currency_rates": [{"currency": "USD", "rate": 75.5}],
        "stock_prices": [{"stock": "AAPL", "currency": "USD", "price": 150.0}],
    }
    assert result == expected_result


@patch("src.utils.load_xlsx_transactions")
def test_error_collect_data_for_main_page(mock_load_xlsx):
    mock_load_xlsx.side_effect = ValueError
    with pytest.raises(ValueError):
        collect_data_for_main_page("2021-12-23 02:00:12")


def test_get_expenses_report(valid_operations):
    result = get_expenses_report(valid_operations)
    expected_result = {
        "total_amount": 29577.8,
        "main": [
            {"category": "Переводы", "amount": 20800.0},
            {"category": "Ж/д билеты", "amount": 2822.8},
            {"category": "Дом и ремонт", "amount": 2500.1},
            {"category": "Супермаркеты", "amount": 1264.76},
            {"category": "Каршеринг", "amount": 965.14},
            {"category": "Различные товары", "amount": 564.0},
            {"category": "Канцтовары", "amount": 349.0},
            {"category": "Остальное", "amount": 312.0},
        ],
        "transfers_and_cash": [{"category": "Переводы", "amount": 20800.0}],
    }
    assert result == expected_result


def test_less_7_categories_get_expenses_report(less_7_categories):
    result = get_expenses_report(less_7_categories)
    expected_result = {
        "total_amount": 985.06,
        "main": [{"category": "Различные товары", "amount": 564.0}, {"category": "Супермаркеты", "amount": 421.06}],
        "transfers_and_cash": [],
    }
    assert result == expected_result


def test_7_categories_get_expenses_report(exactly_7_categories):
    result = get_expenses_report(exactly_7_categories)
    expected_result = {
        "total_amount": 26765.7,
        "main": [
            {"category": "Переводы", "amount": 20800.0},
            {"category": "Ж/д билеты", "amount": 2822.8},
            {"category": "Супермаркеты", "amount": 1264.76},
            {"category": "Каршеринг", "amount": 965.14},
            {"category": "Различные товары", "amount": 564.0},
            {"category": "Канцтовары", "amount": 349.0},
        ],
        "transfers_and_cash": [{"category": "Переводы", "amount": 20800.0}],
    }
    assert result == expected_result


def test_no_categories_get_expenses_report(no_transfers_cash):
    result = get_expenses_report(no_transfers_cash)
    expected_result = {
        "total_amount": 8777.8,
        "main": [
            {"category": "Ж/д билеты", "amount": 2822.8},
            {"category": "Дом и ремонт", "amount": 2500.1},
            {"category": "Супермаркеты", "amount": 1264.76},
            {"category": "Каршеринг", "amount": 965.14},
            {"category": "Различные товары", "amount": 564.0},
            {"category": "Канцтовары", "amount": 349.0},
            {"category": "Фастфуд", "amount": 154.0},
            {"category": "Остальное", "amount": 158.0},
        ],
        "transfers_and_cash": [],
    }
    assert result == expected_result
    assert len(expected_result["main"]) == 8


def test_no_expenses_get_expenses_report(no_expenses):
    result = get_expenses_report(no_expenses)
    expected_result = {"total_amount": 0.0, "main": [], "transfers_and_cash": []}
    assert result == expected_result


def test_invalid_data_get_expenses_report(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных"):
        get_expenses_report(invalid_operations)


def test_get_income_report(valid_operations):
    result = get_income_report(valid_operations)
    expected_result = {"total_amount": 179046.0, "main": [{"category": "Пополнения", "amount": 179046.0}]}
    assert result == expected_result
    assert len(expected_result["main"]) == 1


def test_invalid_data_get_income_report(invalid_operations):
    with pytest.raises(KeyError, match="Ошибка в структуре данных"):
        get_income_report(invalid_operations)


def test_empty_result_get_income_report(no_incomes):
    result = get_income_report(no_incomes)
    expected_result = {"total_amount": 0.0, "main": []}
    assert result == expected_result
    assert len(expected_result["main"]) == 0


@patch("src.utils.load_xlsx_transactions")
@patch("src.utils.filter_transactions_by_period")
@patch("src.utils.get_expenses_report")
@patch("src.utils.get_income_report")
@patch("src.utils.load_user_settings")
@patch("src.utils.get_currencies")
@patch("src.utils.get_stocks")
@patch("src.utils.get_exchange_rates")
@patch("src.utils.get_stock_prices")
def test_collect_data_for_events_page(
    mock_stock_prices,
    mock_exchange_rates,
    mock_stocks,
    mock_currencies,
    mock_user_settings,
    mock_income,
    mock_expenses,
    mock_filter,
    mock_load_xlsx,
):
    mock_load_xlsx.return_value = pd.DataFrame()
    mock_filter.return_value = pd.DataFrame()
    mock_expenses.return_value = {"total_amount": 100, "main": [], "transfers_and_cash": []}
    mock_income.return_value = {"total_amount": 50, "main": []}
    mock_user_settings.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    mock_currencies.return_value = ["USD"]
    mock_stocks.return_value = ["AAPL"]
    mock_exchange_rates.return_value = [{"currency": "USD", "rate": 75.5}]
    mock_stock_prices.return_value = [{"stock": "AAPL", "currency": "USD", "price": 150.0}]

    result = collect_data_for_events_page("2021-12-31 00:00:00")
    expected = {
        "expenses": {"total_amount": 100, "main": [], "transfers_and_cash": []},
        "income": {"total_amount": 50, "main": []},
        "currency_rates": [{"currency": "USD", "rate": 75.5}],
        "stock_prices": [{"stock": "AAPL", "currency": "USD", "price": 150.0}],
    }
    assert result == expected


@patch("src.utils.load_xlsx_transactions")
def test_error_collect_data_for_events_page(mock_load_xlsx):
    mock_load_xlsx.side_effect = ValueError
    with pytest.raises(ValueError):
        collect_data_for_events_page("2021-12-23 02:00:00")
