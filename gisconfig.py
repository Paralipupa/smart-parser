import configparser
import os
from typing import NoReturn

def check_error(func):
    def wrapper(*args):
        try:
            func(*args)
        except:
            pass
    return wrapper

class GisConfig:

    def __init__(self, filename : str):
        self._is_init = False
        if self.is_exist(filename):
            self._config = configparser.ConfigParser()
            self._config.read(filename)
            self._init_configuration()

    def is_exist(self, filename : str) -> bool:
        return os.path.exists(filename)

    def _init_configuration(self) -> NoReturn:

        self._condition_range = ''
        self._condition_column = ''
        self._columns_heading = []
        self._columns_heading_offset = []
        self._row_start = int(self._config['main']['row_start'])
        self._page_name = self._config['main']['page_name']
        self._page_index = int(self._config['main']['page_index'])
        self._max_cols = int(self._config['main']['max_columns'])
        self._max_rows_heading = int(self._config['main']['max_rows_heading'])

        num_cols = int(self._config['main']['columns_count'])
        self._columns_heading = [self._config[f'col_{i}']['pattern'] for i in range(num_cols)]
        for i in range(num_cols):
            self._set_conditions(i)
            self._set_heading_offset(i)
        self._is_init = True

    @check_error
    def _set_conditions(self, i:int):
        if not self._condition_range:
            self._condition_range = self._config[f'col_{i}']['condition_range']
            self._condition_column = self._config[f'col_{i}']['pattern']

    @check_error
    def _set_heading_offset(self, i:int):
        off = {'row':0, 'col':0, 'text':'', 'is_include':False}
        self._columns_heading_offset.append(off)
        self._columns_heading_offset[-1]['row'] = int(self._config[f'col_{i}']['row_offset'])
        self._columns_heading_offset[-1]['col'] = int(self._config[f'col_{i}']['col_offset'])
        self._columns_heading_offset[-1]['text'] = self._config[f'col_{i}']['pattern_offset']
        self._columns_heading_offset[-1]['is_include'] = False if self._config[f'col_{i}']['is_include_offset']=='0' else True
