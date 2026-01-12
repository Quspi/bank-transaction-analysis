import json

import pytest

from src.services import analyze_cashback_categories


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
