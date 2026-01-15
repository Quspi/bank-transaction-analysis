import json
import logging
from datetime import datetime

from requests.exceptions import ConnectionError

from src.utils import collect_data_for_events_page, collect_data_for_main_page

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/views.log", "a", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s: %(name)s: %(funcName)s: %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_main_page_data(date: str) -> str:
    """Возвращает json ответ для страницы `Главная`."""
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        logger.info(f"Дата {date} успешно преобразована")
    except ValueError:
        logger.error(f"Ошибка формата даты {date}", exc_info=True)
        return json.dumps({"error": "Ошибка формата даты. Ожидается YYYY-MM-DD HH:MM:SS"}, ensure_ascii=False)

    try:
        main_page_data = collect_data_for_main_page(date)
        logger.info("Данные для страницы 'Главная' успешно сформированы")
    except (ValueError, ConnectionError) as error:
        logger.error(f"Ошибка: {error}", exc_info=True)
        return json.dumps({"error": str(error)}, ensure_ascii=False)

    result = json.dumps(main_page_data, indent=4, ensure_ascii=False)
    logger.info("Данные успешно преобразованы в JSON ответ")
    return result


def get_events_page_data(date: str, period: str = "M") -> str:
    """Возвращает json ответ для страницы `События`."""
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        logger.info(f"Дата {date} успешно преобразована")
    except ValueError:
        logger.error(f"Ошибка формата даты {date}", exc_info=True)
        return json.dumps({"error": "Ошибка формата даты. Ожидается YYYY-MM-DD HH:MM:SS"}, ensure_ascii=False)

    try:
        events_page_data = collect_data_for_events_page(date, period)
        logger.info("Данные для страницы 'События' успешно сформированы")
    except (ValueError, ConnectionError) as error:
        logger.error(f"Ошибка: {error}", exc_info=True)
        return json.dumps({"error": str(error)}, ensure_ascii=False)

    result = json.dumps(events_page_data, indent=4, ensure_ascii=False)
    logger.info("Данные успешно преобразованы в JSON ответ")
    return result
