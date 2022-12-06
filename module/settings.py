import logging, os

# ENCONING = 'utf-8'
ENCONING = 'windows-1251'

DOCUMENTS = 'accounts pp pp_charges pp_service pu puv'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_LOG = os.path.join(BASE_DIR, 'logs')
PATH_OUTPUT = os.path.join(BASE_DIR, 'output')
PATH_CONFIG = os.path.join(BASE_DIR, 'config')
PATH_TMP = os.path.join(BASE_DIR, 'tmp')

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

db_logger = logging.getLogger('parser')

