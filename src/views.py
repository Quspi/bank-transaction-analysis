import json
import logging
from datetime import datetime

from requests.exceptions import ConnectionError

from src.utils import collect_data_for_main_page

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/utils.log", "a", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s: %(name)s: %(funcName)s: %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_main_page_data(date: str) -> str:
    """Возвращает json ответ для страницы `Главная`."""
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return json.dumps({"error": "Неверный формат даты. Ожидается YYYY-MM-DD HH:MM:SS"}, ensure_ascii=False)

    try:
        main_page_data = collect_data_for_main_page(date)
    except (ValueError, ConnectionError) as error:
        return json.dumps({"error": str(error)}, ensure_ascii=False)

    result = json.dumps(main_page_data, indent=4, ensure_ascii=False)
    return result
