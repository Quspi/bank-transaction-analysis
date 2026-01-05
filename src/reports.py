import logging
from typing import Any, Callable, Optional

import pandas as pd

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
