import os
from logging import config as lgconfig

ENCONING = "windows-1251"

DOCUMENTS = "contracts accounts pp pp_charges pp_service pu puv bank_accounts"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_LOG = os.path.join(BASE_DIR, "logs")
if not os.path.exists(PATH_LOG):
    os.makedirs(PATH_LOG)
PATH_OUTPUT = os.path.join(BASE_DIR, "output")
PATH_DOWNLOAD = os.path.join(BASE_DIR, "download")
PATH_CONFIG = os.path.join(BASE_DIR, "config")
PATH_TMP = os.path.join(BASE_DIR, "tmp")

ERROR_LOG_FILENAME = os.path.join(BASE_DIR, "logs", "error.log")
WARNING_LOG_FILENAME = os.path.join(BASE_DIR, "logs", "warning.log")
DEBUG_LOG_FILENAME = os.path.join(BASE_DIR, "logs", "debug.log")
INFO_LOG_FILENAME = os.path.join(BASE_DIR, "logs", "info.log")
CONFIGURATION_FILE= os.path.join(PATH_CONFIG, "configuration.json")

POS_INDEX_VALUE = 0
POS_INDEX_IS_NEGATIVE = 1
POS_INDEX_TITLE = 2

POS_NUMERIC_VALUE = 0
POS_NUMERIC_IS_ABSOLUTE = 1
POS_NUMERIC_IS_NEGATIVE = 2

POS_VALUE = 0
POS_PAGE_VALUE = 0
POS_PAGE_IS_FIX = 1

IS_MESSAGE_PRINT = True
IS_DELETE_TMP = False

COLOR_CONSOLE = {
    "end": "\033[0m",
    "cyan": "\033[36m",
    "red": "\033[91m",
    "magenta": "\033[35m",
}
# регулярное выражение для определения капитального ремонта  по названию файлов и полей
REG_KP_XLS = "\sкап|кап(?:.+)?рем|кап[.]|\sкр\s|кр_|Капрем"
REG_ACCOUNT_NUMBER_BANK = "[0-9]{20}"
REG_BIK_BANK = "[0-9]{9}"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "InfoFilter": {
            "()": "module.logger.InfoFilter",
        },
        "HTTPFilter": {
            "()": "module.logger.HTTPFilter",
        },
        "DebugFilter": {
            "()": "module.logger.DebugFilter",
        },
        "WarningFilter": {
            "()": "module.logger.WarningFilter",
        },
        "ErrorFilter": {
            "()": "module.logger.ErrorFilter",
        },
    },
    "formatters": {
        "default": {
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "format": "%(asctime)s - %(message)s",
        },
        "simple": {
            "()": "module.logger.CustomFormatter",
            "datefmt": "%d-%m-%Y %H:%M:%S",
            "format": "%(asctime)s - {}%(message)s{}",
        },
        "verbose": {
            "()": "module.logger.CustomFormatter",
            "datefmt": "%d-%m-%Y %H:%M:%S",
            "format": "%(asctime)s - {}%(message)s{} %(exc_info)s %(name)s:%(lineno)d %(exc_info)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "format": """
                    \nasctime: %(asctime)s
                    \nname: %(name)s
                    \nlineno: %(lineno)d
                """,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "filters": ["InfoFilter"],
            "formatter": "simple",
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "logfile": {
            "filters": ["InfoFilter"],
            "formatter": "default",
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "encoding": ENCONING,
            "filename": INFO_LOG_FILENAME,
            "maxBytes": 100 * 2**10,
            "backupCount": 2,
        },
        "debug": {
            "filters": ["DebugFilter"],
            "formatter": "default",
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "encoding": ENCONING,
            "filename": DEBUG_LOG_FILENAME,
            "maxBytes": 100 * 2**10,
            "backupCount": 2,
            "delay": True,
        },
        "warning": {
            "filters": ["WarningFilter"],
            "formatter": "verbose",
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "encoding": ENCONING,
            "filename": WARNING_LOG_FILENAME,
            "maxBytes": 100 * 2**10,
            "backupCount": 2,
            "delay": True,
        },
        "error": {
            "filters": ["ErrorFilter"],
            "formatter": "verbose",
            "level": "WARNING",
            "class": 'logging.FileHandler',
            "encoding": ENCONING,
            "filename": ERROR_LOG_FILENAME,
            # "maxBytes": 100 * 2**10,
            # "backupCount": 2,
            # "delay": True,
            "mode": "w",
        },
        "json": {
            "filters": ["ErrorFilter"],
            "formatter": "json",
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "encoding": ENCONING,
            "filename": ERROR_LOG_FILENAME,
            "maxBytes": 100 * 2**10,
            "backupCount": 2,
            "delay": True,
        },
        "http_handler": {
            "filters": ["HTTPFilter"],
            "formatter": "verbose",
            "class": "module.logger.CustomHTTPHandler",
            "host": "localhost:5000",
            "url": "http://localhost:5000/list/logs/info.log",
            "credentials": (os.environ.get("USERNAME"), os.environ.get("PASSWORD")),
            "method": "GET",
            "secure": True,
        },
    },
    "loggers": {
        "debug": {
            "level": "DEBUG",
            "handlers": ["console", "debug"],
            "propagate": False,
        },
        "asyncio": {
            "level": "WARNING",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "console",
            "logfile",
            "warning",
            "debug",
            "error",
            "json",
            # "http_handler"
        ],
    },
}

lgconfig.dictConfig(LOGGING)

if os.path.exists(os.path.join(os.path.dirname(__file__), "settings_local.py")):
    from module.settings_local import *
