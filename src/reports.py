import datetime
import logging
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/reports.log", "a", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s: %(name)s: %(funcName)s: %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def save_report(file_name: Optional[str] = None) -> Callable:
    """Сохраняет результат работы функций-отчетов в JSON файл."""

    def decorator(function: Callable) -> Callable:

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            filename = file_name or f"{function.__name__}"
            result = function(*args, **kwargs)

            if isinstance(result, pd.DataFrame):
                result.to_json(f"data/{filename}_report.json", orient="records", indent=4, force_ascii=False)

            return result

        return wrapper

    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Рассчитывает траты по выбранной категории за последние 3 месяца с начальной даты, и возвращает DataFrame
    состоящий из Периода и Суммы за период. Если date (ДД-ММ-ГГГГ) не указана, то берется текущая дата."""
    if date is None:
        end_date = datetime.datetime.now()
    else:
        end_date = datetime.datetime.strptime(date, "%d-%m-%Y")
    start_date = end_date - relativedelta(months=3)
    logger.info(f"Расчет по категории {category}, с {start_date} по {end_date}")

    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_df = transactions.loc[
            (transactions["Категория"] == category)
            & (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Статус"] == "OK")
            & (transactions["Валюта операции"] == "RUB")
            & (transactions["Сумма операции"] < 0)
        ].copy()
        filtered_df["Сумма операции"] = filtered_df["Сумма операции"].abs()

        if filtered_df.empty:
            return pd.DataFrame(columns=["Период", "Сумма"])

    except ValueError:
        logger.error(f"Некорректный формат даты {date}", exc_info=True)
        raise ValueError("Некорректный формат даты.")

    except KeyError:
        logger.error("Ошибка в структуре данных DF", exc_info=True)
        raise KeyError("Ошибка в структуре данных.")

    filtered_df["Период"] = filtered_df["Дата операции"].dt.strftime("%Y-%m")
    grouped = filtered_df.groupby("Период")["Сумма операции"].sum().reset_index()
    result_df: pd.DataFrame = grouped.rename(columns={"Сумма операции": "Сумма"})

    logger.info(f"Рассчитаны траты по категории {category}")
    return result_df
