import json
import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/services.log", "a", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s: %(name)s: %(funcName)s: %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def analyze_cashback_categories(data: list[dict], year: int, month: int) -> str:
    """Вычислят 3 наиболее выгодных категории для выбора повышенного кэшбэка за указанные год и месяц."""
    data_df = pd.DataFrame(data)
    logger.info("Данные преобразованы в DF")

    try:
        data_df["Дата операции"] = pd.to_datetime(data_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_df = data_df.loc[
            (data_df["Дата операции"].dt.year == year)
            & (data_df["Дата операции"].dt.month == month)
            & (data_df["Сумма операции"] < 0)
            & (data_df["Статус"] == "OK")
            & (data_df["Валюта платежа"] == "RUB")
            & (~data_df["Категория"].isin(["Наличные", "Переводы"]))
        ].copy()
        logger.info(f"Данные отфильтрованы год {year}, месяц {month}")
        filtered_df["Сумма операции"] = filtered_df["Сумма операции"].abs()

    except KeyError:
        logger.error("Ошибка в структуре данных DF", exc_info=True)
        raise KeyError("Ошибка в структуре данных.")

    group_by_category = filtered_df.groupby("Категория")["Сумма операции"].sum()
    top_category = group_by_category.nlargest(3)

    category_dict = {}

    for category, expense in top_category.items():
        category_dict[category] = round(float(expense) / 100, 2)
    logger.info(f"Получено {len(category_dict)} выгодных категорий")

    if len(category_dict) == 0:
        logger.warning("Не найдено транзакций за выбранный период")

    result = json.dumps(category_dict, indent=4, ensure_ascii=False)
    logger.info("Данные сформированы в JSON ответ")
    return result


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """Рассчитывает сумму, которую можно отложить путём округления трат до заданного предела.
    Month: строка в формате 'YYYY-MM'"""
    if limit <= 0:
        logger.error(f"Ошибка, {limit} должен быть положительным числом")
        raise ValueError("limit должен быть положительным числом.")

    total_saved = 0.0

    for transaction in transactions:
        if "Дата операции" not in transaction or "Сумма операции" not in transaction:
            logger.warning(f"Некорректная структура транзакции {transaction}")
            continue
        elif not transaction["Дата операции"].startswith(month):
            continue
        elif transaction["Сумма операции"] >= 0:
            continue

        amount = abs(transaction["Сумма операции"])
        remainder = amount % limit

        if remainder > 0:
            rounded = amount + (limit - remainder)
        else:
            rounded = amount

        total_saved += rounded - amount

    logger.info(f"Рассчитанная сумма округления {total_saved}")
    return round(total_saved, 2)
