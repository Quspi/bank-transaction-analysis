import datetime
from typing import Union

import pandas as pd


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


def load_xlsx_transactions(file_path: str, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    """Получает данные о транзакциях из xlsx файла и возвращает DataFrame."""
    transactions_data = pd.read_excel(file_path, sheet_name=sheet_name)
    return transactions_data


def calculate_card_statistics(df: pd.DataFrame) -> list[dict]:
    """Рассчитывает статистику по каждой карте: сумма расходов и кешбэк в рублях."""
    expense = df.loc[(df["Статус"] == "OK") & (df["Сумма операции"] < 0) & (df["Валюта операции"] == "RUB")].copy()
    expense["Сумма операции"] = expense["Сумма операции"].abs()
    expenses_by_cards = expense.groupby("Номер карты")["Сумма операции"].sum()

    result_list = []

    for card_number, expense in expenses_by_cards.items():
        result_list.append(
            {"last_digits": str(card_number)[-4:], "total_spent": expense, "cashback": round(expense / 100, 2)}
        )

    return result_list


if __name__ == "__main__":
    transactions = load_xlsx_transactions("data/operations.xlsx")
    print(calculate_card_statistics(transactions))
