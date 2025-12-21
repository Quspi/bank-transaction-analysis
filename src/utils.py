import datetime


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


if __name__ == "__main__":
    pass
