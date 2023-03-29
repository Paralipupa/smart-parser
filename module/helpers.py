import datetime, re
import logging
from typing import NoReturn, Union
from datetime import datetime
from .exceptions import InnMismatchException, FatalException
from .settings import IS_MESSAGE_PRINT, POS_NUMERIC_VALUE, POS_NUMERIC_IS_ABSOLUTE

logger = logging.getLogger(__name__)


def timing(start_message: str = "", end_message: str = "Завершено"):
    def wrap(f):
        def inner(*args, **kwargs):
            if start_message:
                logger.info(start_message)
            time1 = datetime.datetime.now()
            ret = f(*args, **kwargs)
            time2 = datetime.datetime.now()
            if end_message:
                logger.info("{0} ({1})".format(end_message, (time2 - time1)))
            return ret

        return inner

    return wrap


def fatal_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InnMismatchException as ex:
            logger.exception("Inn error")
            raise InnMismatchException
        except Exception as ex:
            logger.exception("Fatal error")
            raise FatalException("")

    return wrapper


def warning_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as ex:
            logger.exception("Warning")
            return None

    return wrapper


def print_message(msg: str, end: str = "\n", flush: bool = False) -> NoReturn:
    if IS_MESSAGE_PRINT:
        print(msg, end=end, flush=flush)


def regular_calc(pattern: str, value: str) -> str:
    try:
        result = re.search(pattern, value.replace("\n", "").strip(), re.IGNORECASE)
        if result is None or result.group(0).find("error") != -1:
            return None
        else:
            return result.group(0).strip()
    except Exception as ex:
        logger.exception("Regular error")
        return f"error in regular: '{pattern}' ({str(ex)})"


def get_value_str(value: str, pattern: str) -> str:
    return regular_calc(pattern, value)


def get_value_int(value: Union[list, str]) -> int:
    try:
        if value:
            if isinstance(value, list):
                return value[0]
            elif isinstance(value, str):
                return int(value.replace(",", ".").replace(" ", "")).replace(
                    chr(160), ""
                )
        else:
            return 0
    except:
        return 0


def get_value_float(value: str) -> float:
    try:
        if value:
            if isinstance(value, str):
                return float(
                    value.replace(",", ".").replace(" ", "").replace(chr(160), "")
                )
            else:
                return 0
        else:
            return 0
    except:
        return 0


def get_value_range(value: list, count: int = 0) -> list:
    try:
        if value:
            return value
        else:
            return [(i, True) for i in range(count)]
    except:
        return [(i, True) for i in range(count)]


def get_months() -> dict:
    return {
        "январ": "01",
        "феврал": "02",
        "март": "03",
        "апрел": "04",
        "май": "05",
        "мая": "05",
        "июн": "06",
        "июл": "07",
        "август": "08",
        "сентябр": "09",
        "октябр": "10",
        "ноябр": "11",
        "декабр": "12",
    }


def get_absolute_index(items: tuple, current: int) -> int:
    index = (
        items[POS_NUMERIC_VALUE]
        if items[POS_NUMERIC_IS_ABSOLUTE]
        else items[POS_NUMERIC_VALUE] + current
    )
    return index
