import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/utils.log", "a", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s: %(name)s: %(funcName)s: %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def analyze_cashback_categories(data: pd.DataFrame, year: int, month: int) -> str:
    try:
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_df = data.loc[
            (data["Дата операции"].dt.year == year)
            & (data["Дата операции"].dt.month == month)
            & (data["Сумма операции"] < 0)
            & (data["Статус"] == "OK")
            & (data["Валюта платежа"] == "RUB")
            & (~data["Категория"].isin(["Наличные", "Переводы"]))
        ].copy()
        filtered_df["Сумма операции"] = filtered_df["Сумма операции"].abs()

    except KeyError:
        raise KeyError("Ошибка в структуре данных.")

    group_by_category = filtered_df.groupby("Категория")["Сумма операции"].sum()
    top_category = group_by_category.nlargest(3)

    category_dict = {}

    for category, expense in top_category.items():
        category_dict[category] = round(float(expense) / 100, 2)

    result = json.dumps(category_dict, indent=4, ensure_ascii=False)
    return result
