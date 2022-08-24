import logging

# ENCONING = 'utf-8'
ENCONING = 'windows-1251'

DOCUMENTS = 'accounts pp pp_charges pp_service pu puv'

PATH_LOG = 'logs'
PATH_OUTPUT = 'output'
PATH_CONFIG = 'config'
PATH_TMP = 'tmp'

POS_INDEX_VALUE = 0
POS_INDEX_IS_NEGATIVE = 1

POS_NUMERIC_VALUE = 0
POS_NUMERIC_IS_ABSOLUTE = 1
POS_NUMERIC_IS_NEGATIVE = 2

POS_VALUE = 0
POS_PAGE_VALUE = 0
POS_PAGE_IS_FIX = 1

db_logger = logging.getLogger('parser')

