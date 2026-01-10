import json
from unittest.mock import mock_open, patch

import pytest
from freezegun import freeze_time

from src.utils import get_currencies, get_greetings, load_user_settings


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
