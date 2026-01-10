import json
from unittest.mock import patch

import requests

from src.views import get_events_page_data, get_main_page_data


@patch("src.views.collect_data_for_main_page")
def test_get_main_page_data(mock_collect_data):
    mock_data = {
        "greeting": "Добрый день",
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": [],
    }
    mock_collect_data.return_value = mock_data
    result = get_main_page_data("2021-12-31 00:00:00")
    expected = json.dumps(mock_data, indent=4, ensure_ascii=False)
    assert result == expected


def test_invalid_date_get_main_page_data():
    result = get_main_page_data("31-12-2921")
    expected_result = json.dumps({"error": "Ошибка формата даты. Ожидается YYYY-MM-DD HH:MM:SS"}, ensure_ascii=False)
    assert result == expected_result


@patch("src.views.collect_data_for_main_page")
def test_value_error_get_main_page_data(mock_collect_data):
    mock_collect_data.side_effect = ValueError("ValueError")
    result = get_main_page_data("2021-12-31 00:00:00")
    expected_result = json.dumps({"error": "ValueError"}, ensure_ascii=False)
    assert result == expected_result


@patch("src.views.collect_data_for_main_page")
def test_connection_error_get_main_page_data(mock_collect_data):
    mock_collect_data.side_effect = requests.exceptions.ConnectionError("ConnectionError")
    result = get_main_page_data("2021-12-31 00:00:00")
    expected_result = json.dumps({"error": "ConnectionError"}, ensure_ascii=False)
    assert result == expected_result


@patch("src.views.collect_data_for_events_page")
def test_get_events_page_data(mock_collect_data):
    mock_data = {
        "expenses": {"total_amount": 100, "main": [], "transfers_and_cash": []},
        "income": {"total_amount": 50, "main": []},
        "currency_rates": [{"currency": "USD", "rate": 75.5}],
        "stock_prices": [{"stock": "AAPL", "currency": "USD", "price": 150.0}],
    }
    mock_collect_data.return_value = mock_data
    result = get_events_page_data("2020-10-26 16:51:06")
    expected = json.dumps(mock_data, indent=4, ensure_ascii=False)
    assert result == expected


def test_invalid_date_get_events_page_data():
    result = get_events_page_data("31-12-2921")
    expected_result = json.dumps({"error": "Ошибка формата даты. Ожидается YYYY-MM-DD HH:MM:SS"}, ensure_ascii=False)
    assert result == expected_result


@patch("src.views.collect_data_for_events_page")
def test_value_error_get_events_page_data(mock_collect_data):
    mock_collect_data.side_effect = ValueError("ValueError")
    result = get_events_page_data("2021-12-31 00:00:00")
    expected_result = json.dumps({"error": "ValueError"}, ensure_ascii=False)
    assert result == expected_result


@patch("src.views.collect_data_for_events_page")
def test_connection_get_events_page_data(mock_collect_data):
    mock_collect_data.side_effect = requests.exceptions.ConnectionError("ConnectionError")
    result = get_events_page_data("2021-12-31 00:00:00")
    expected_result = json.dumps({"error": "ConnectionError"}, ensure_ascii=False)
    assert result == expected_result
