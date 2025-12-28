import json
from datetime import datetime

from requests.exceptions import ConnectionError

from src.utils import collect_data_for_main_page


def get_main_page_data(date: str) -> str:
    """Возвращает json ответ для страницы `Главная`."""
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return json.dumps({"error": "Неверный формат даты. Ожидается YYYY-MM-DD HH:MM:SS"})

    try:
        main_page_data = collect_data_for_main_page(date)
    except (ValueError, ConnectionError) as error:
        return json.dumps({"error": str(error)})

    result = json.dumps(main_page_data, indent=4)
    return result
