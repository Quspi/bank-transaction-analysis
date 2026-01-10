import pytest
from freezegun import freeze_time

from src.utils import get_greetings


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
