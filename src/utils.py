import datetime
import json
import logging
import os
import time
from typing import Any, Union

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TRANSACTIONS_PATH = os.path.join(BASE_DIR, "data", "operations.xlsx")
USER_SETTINGS_PATH = os.path.join(BASE_DIR, "user_settings.json")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/utils.log", "a", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s: %(name)s: %(funcName)s: %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_greetings() -> str:
    """Возвращает приветствие в зависимости от текущего времени суток."""
    now_hour = datetime.datetime.now().hour

    if 5 <= now_hour < 11:
        greeting = "Доброе утро"
    elif 11 <= now_hour < 16:
        greeting = "Добрый день"
    elif 16 <= now_hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    logger.info(f"Сгенерировано приветствие {greeting} для часа {now_hour}")
    return greeting


def load_user_settings(file_path: str) -> dict[str, list[str]]:
    """Загружает настройки пользователя из json файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            logger.info(f"Открыт файл {file_path}")
            try:
                user_settings: dict[str, list[str]] = json.load(file)
                logger.info(f"Загружены настройки пользователя из {file_path}")
            except json.JSONDecodeError as error:
                logger.error(f"Ошибка декодирования {error}", exc_info=True)
                raise ValueError("Файл повреждён или пуст.")

            if "user_currencies" in user_settings and "user_stocks" in user_settings:
                logger.info(f"currencies: {user_settings['user_currencies']}, stocks: {user_settings['user_stocks']}")
                return user_settings
            else:
                logger.error(f"Ошибка в структуре данных файла {file_path}", exc_info=True)
                raise ValueError("Ошибка в структуре данных.")

    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден или удален", exc_info=True)
        raise ValueError("Файл не найден или удален.")


def get_currencies(user_settings: dict[str, list[str]]) -> list[str]:
    """Получает список валют пользователя для отслеживания курса."""
    result = user_settings["user_currencies"]
    logger.info(f"{len(result)} валют для отслеживания")
    return result


def get_stocks(user_settings: dict[str, list[str]]) -> list[str]:
    """Получает список акций пользователя для отслеживания курса."""
    result = user_settings["user_stocks"]
    logger.info(f"{len(result)} акций для отслеживания")
    return result


def load_xlsx_transactions(file_path: str, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    """Получает данные о транзакциях из xlsx файла и возвращает DataFrame."""
    try:
        transactions_data = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(f"Транзакции успешно загружены из {file_path}, лист {sheet_name}")
        return transactions_data

    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден или удален", exc_info=True)
        raise ValueError("Файл не найден или удален.")

    except pd.errors.EmptyDataError:
        logger.error(f"Файл {file_path} не содержит данные", exc_info=True)
        raise ValueError("Файл не содержит данные.")


def calculate_card_statistics(df: pd.DataFrame) -> list[dict]:
    """Рассчитывает статистику по каждой карте: сумма расходов и кешбэк в рублях."""
    try:
        expense = df.loc[(df["Статус"] == "OK") & (df["Сумма операции"] < 0) & (df["Валюта операции"] == "RUB")].copy()
        expense["Сумма операции"] = expense["Сумма операции"].abs()
        logger.info(f"Отфильтровано {len(expense)} транзакций")
        expenses_by_cards = expense.groupby("Номер карты")["Сумма операции"].sum()

    except KeyError:
        logger.error("Ошибка в структуре данных DF", exc_info=True)
        raise KeyError("Ошибка в структуре данных.")

    result_list = []

    for card_number, expense in expenses_by_cards.items():
        result_list.append(
            {
                "last_digits": str(card_number)[-4:],
                "total_spent": round(expense, 2),
                "cashback": round(expense / 100, 2),
            }
        )

    logger.info(f"Успешно рассчитана статистика по картам, всего карт: {len(result_list)}")
    return result_list


def get_top_transactions(df: pd.DataFrame) -> list[dict]:
    """Рассчитывает топ 5 транзакций по сумме платежа."""
    try:
        filtered_df = df.loc[(df["Статус"] == "OK") & (df["Валюта операции"] == "RUB")]
        filtered_df["abs_amount"] = filtered_df["Сумма операции"].abs()
        filtered_df["Дата операции"] = filtered_df["Дата операции"].dt.strftime("%d.%m.%Y")
        logger.info(f"Отфильтровано {len(filtered_df)} транзакций")
        top_5_df = filtered_df.nlargest(5, "abs_amount")

    except KeyError:
        logger.error("Ошибка в структуре данных DF", exc_info=True)
        raise KeyError("Ошибка в структуре данных.")

    result = (
        top_5_df[["Дата операции", "Сумма операции", "Категория", "Описание"]]
        .rename(
            columns={
                "Дата операции": "date",
                "Сумма операции": "amount",
                "Категория": "category",
                "Описание": "description",
            }
        )
        .to_dict(orient="records")
    )

    logger.info("Успешно рассчитаны топ 5 транзакций по сумме платежа")
    return result


def filter_transactions_by_month(df: pd.DataFrame, date_string: str) -> pd.DataFrame:
    """Возвращает транзакции с начала месяца (1-е число) до указанной даты включительно."""
    end_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1)

    try:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filter_by_month = df.loc[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

    except KeyError:
        raise KeyError("Ошибка в структуре данных.")

    if filter_by_month.empty:
        raise ValueError("Транзакций за указанный период не найдено.")

    return filter_by_month


def get_exchange_rates(currencies: list[str]) -> list[dict]:
    """Получает курсы валют в RUB указанные в currencies."""
    result: list[dict] = []

    if not currencies:
        return result

    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.HTTPError as error:
        status_code = error.response.status_code
        raise ConnectionError(f"HTTP ошибка, код ошибки: {status_code}.")
    except requests.exceptions.ConnectionError as error:
        raise ConnectionError(f"Ошибка соединения: {error}.")
    except requests.exceptions.Timeout as error:
        raise TimeoutError(f"Таймаут запроса: {error}.")

    currencies_data = response.json().get("Valute", {})

    for currency in currencies:
        if currency in currencies_data:
            result.append(
                {
                    "currency": currencies_data[currency]["CharCode"],
                    "rate": round(currencies_data[currency]["Value"], 2),
                }
            )

    return result


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Получает стоимость акций компаний указанных в stocks."""
    result: list[dict] = []

    if not stocks:
        return result

    url = "https://www.alphavantage.co/query"
    api_key = os.getenv("API_KEY")

    for stock in stocks:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            time.sleep(12)

        except requests.exceptions.HTTPError:
            time.sleep(12)
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(12)
            continue
        except requests.exceptions.Timeout:
            time.sleep(12)
            continue

        stock_data = response.json().get("Global Quote")

        if not stock_data:
            continue

        result.append(
            {"stock": stock_data["01. symbol"], "currency": "USD", "price": round(float(stock_data["05. price"]), 2)}
        )

    return result


def collect_data_for_main_page(date: str) -> dict[str, Any]:
    """Собирает данные о транзакциях в словарь для страницы `Главная`."""
    greeting = get_greetings()
    transactions = load_xlsx_transactions(TRANSACTIONS_PATH)
    filtered_by_date = filter_transactions_by_month(transactions, date)
    cards = calculate_card_statistics(filtered_by_date)
    top_transactions = get_top_transactions(filtered_by_date)

    user_settings = load_user_settings(USER_SETTINGS_PATH)
    user_currencies = get_currencies(user_settings)
    user_stocks = get_stocks(user_settings)

    currency_rates = get_exchange_rates(user_currencies)
    stock_prices = get_stock_prices(user_stocks)

    result_dict = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return result_dict
