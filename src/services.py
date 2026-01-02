import json
import logging

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
