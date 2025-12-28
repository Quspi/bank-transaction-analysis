import datetime
import os
from typing import Union
import json
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def get_greetings() -> str:
    """Возвращает приветствие в зависимости от текущего времени суток."""
    now_hour = datetime.datetime.now().hour

    if 5 <= now_hour < 11:
        return "Доброе утро"
    elif 11 <= now_hour < 16:
        return "Добрый день"
    elif 16 <= now_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def load_user_settings(file_path: str) -> dict[str, list[str]]:
    """Загружает настройки пользователя из json файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                user_settings = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Файл повреждён или пуст.")

            if "user_currencies" in user_settings and "user_stocks" in user_settings:
                return user_settings
            else:
                raise ValueError("Ошибка в структуре данных.")

    except FileNotFoundError:
        raise ValueError("Файл не найден или удален.")


def get_currencies(user_settings: dict[str, list[str]]) -> list[str]:
    """Получает список валют пользователя для отслеживания курса."""
    result = user_settings["user_currencies"]
    return result


def get_stocks(user_settings: dict[str, list[str]]) -> list[str]:
    """Получает список акций пользователя для отслеживания курса."""
    result = user_settings["user_stocks"]
    return result


def load_xlsx_transactions(file_path: str, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    """Получает данные о транзакциях из xlsx файла и возвращает DataFrame."""
    try:
        transactions_data = pd.read_excel(file_path, sheet_name=sheet_name)
        return transactions_data

    except FileNotFoundError:
        raise ValueError("Файл не найден или удален.")

    except pd.errors.EmptyDataError:
        raise ValueError("Файл не содержит данные.")


def calculate_card_statistics(df: pd.DataFrame) -> list[dict]:
    """Рассчитывает статистику по каждой карте: сумма расходов и кешбэк в рублях."""
    try:
        expense = df.loc[(df["Статус"] == "OK") & (df["Сумма операции"] < 0) & (df["Валюта операции"] == "RUB")].copy()
        expense["Сумма операции"] = expense["Сумма операции"].abs()
        expenses_by_cards = expense.groupby("Номер карты")["Сумма операции"].sum()

    except KeyError:
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

    return result_list


def get_top_transactions(df: pd.DataFrame) -> list[dict]:
    """Рассчитывает топ 5 транзакций по сумме платежа."""
    try:
        filtered_df = df.loc[(df["Статус"] == "OK") & (df["Валюта операции"] == "RUB")]
        filtered_df["abs_amount"] = filtered_df["Сумма операции"].abs()
        filtered_df["Дата операции"] = filtered_df["Дата операции"].dt.strftime("%d.%m.%Y")
        top_5_df = filtered_df.nlargest(5, "abs_amount")

    except KeyError:
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
    """Получает стоимость акций компаний указанных в stocks (до 5 акций за раз)."""
    result: list[dict] = []

    if len(stocks) > 5:
        raise ValueError("Можно загрузить стоимость не более 5 акций за раз.")

    if not stocks:
        return result

    url = "https://www.alphavantage.co/query"
    api_key = os.getenv("API_KEY")

    for stock in stocks:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

        except requests.exceptions.HTTPError:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            continue

        stock_data = response.json().get("Global Quote")

        if not stock_data:
            continue

        result.append(
            {"stock": stock_data["01. symbol"], "currency": "USD", "price": round(float(stock_data["05. price"]), 2)}
        )

    return result


if __name__ == "__main__":
    transactions = load_xlsx_transactions("data/operations.xlsx")
    filtered = filter_transactions_by_month(transactions, "2021-12-22 21:40:59")
    load_user_settings("user_settings.json")
