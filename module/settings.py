import logging, os

ENCONING = 'windows-1251'

DOCUMENTS = 'accounts pp pp_charges pp_service pu puv bank_accounts'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_LOG = os.path.join(BASE_DIR, 'logs')
PATH_OUTPUT = os.path.join(BASE_DIR, 'output')
PATH_DOWNLOAD = os.path.join(BASE_DIR, 'download')
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
IS_DELETE_TMP=False

db_logger = logging.getLogger('parser')

if os.path.exists(os.path.join(os.path.dirname(__file__),'settings_local.py')):
    from module.settings_local import *
