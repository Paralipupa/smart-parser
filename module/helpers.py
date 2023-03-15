import datetime
import logging
from datetime import datetime
from .exceptions import InnMismatchException, FatalException
from .settings import IS_MESSAGE_PRINT

logger = logging.getLogger(__name__)

def timing(start_message:str="", end_message:str = "Завершено"):
    def wrap(f):
        def inner(*args, **kwargs):
            if start_message: logger.info(start_message)
            time1 = datetime.datetime.now()
            ret = f(*args, **kwargs)
            time2 = datetime.datetime.now()
            if end_message: logger.info("{0} ({1})".format(end_message, (time2 - time1)))
            return ret
        return inner
    return wrap

def fatal_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InnMismatchException as ex:
            logger.exception('Inn error')
            raise  InnMismatchException
        except Exception as ex:
            logger.exception('Fatal error')
            raise FatalException('')
    return wrapper


def warning_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as ex:
            logger.exception('Warning')
            return None
    return wrapper

def print_message(msg: str, end: str = '\n', flush: bool = False):
    if IS_MESSAGE_PRINT:
        print(msg, end=end, flush=flush)
