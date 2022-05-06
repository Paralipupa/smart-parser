import configparser
import os
from typing import NoReturn
import logging

def check_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except:
            logging.warning('error in func: {}. skip'.format(func))
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

        self._condition_team:str = ''  #условие начала новой области (регулярное выражение)
        self._condition_column:int = '' # колонка в которой просматривается условие области
        self._columns_heading:list[str] = []  # список заголовков колонок таблицы 
        self._columns_heading_offset:list[dict] = [] #список "якорей" заголовков таблицы 
        self._row_start:int = int(self._config['main']['row_start'])    #
        self._page_name:str = self._config['main']['page_name']         #
        self._page_index:int = int(self._config['main']['page_index'])  #
        self._max_cols:int = int(self._config['main']['max_columns'])   #максимальное кол-во просматриваемых колонок 
        self._max_rows_heading:int = int(self._config['main']['max_rows_heading'])#максимальное кол-во строк до таблицы
        self._documents:list[dict] = [] #список документов (настроек)
        self._parameters = dict()

        self._set_parameter_period()

        num_cols = int(self._config['main']['columns_count'])
        self._columns_heading = [self._config[f'col_{i}']['pattern'] for i in range(num_cols)]
        for i in range(num_cols):
            self._set_conditions(i)
            self._set_heading_offset(i)

        num_cols = int(self._config['main']['documents_count'])
        for i in range(num_cols):
            self._set_documents(i)
            
        self._is_init = True

    
    @check_error
    def _set_parameter_period(self):
        count = int(self._config['parameters']['count'])
        for i in range(count):
            self._parameters[self._config[f'param_{i}']['name']] = {
                'row' : self._get_range(self._config[f'param_{i}']['row']),
                'col' : self._get_range(self._config[f'param_{i}']['column']),
                'pattern' : self._config[f'param_{i}']['pattern'],
            }

    @check_error
    def _set_conditions(self, i:int) -> NoReturn:
        if not self._condition_team:
            self._condition_team = self._config[f'col_{i}']['condition_team']
            self._condition_column = self._config[f'col_{i}']['pattern']

    @check_error
    def _set_heading_offset(self, i:int):
        off = {'row':[0], 'col':[0], 'text':'', 'is_include':False}
        self._columns_heading_offset.append(off)
        self._columns_heading_offset[-1]['row'] = self._get_range(self._config[f'col_{i}']['row_offset'])
        self._columns_heading_offset[-1]['col'] = self._get_range(self._config[f'col_{i}']['col_offset'])
        self._columns_heading_offset[-1]['text'] = self._config[f'col_{i}']['pattern_offset']
        self._columns_heading_offset[-1]['is_include'] = False if self._config[f'col_{i}']['is_include_offset']=='0' else True

    @check_error
    def _set_documents(self, i:int) -> NoReturn:
        doc = dict()
        doc['name'] = self._config[f'doc_{i}']['name']
        doc['attributes'] = list()
        num_count = int(self._config[f'doc_{i}']['attribute_count'])
        for i in range(num_count):
            attr = dict()
            attr['name'] = self._config[f'{doc["name"]}_{i}']['name'] #имя аттрибута
            attr['pattern'] =  self._config[f'{doc["name"]}_{i}']['pattern'] #шаблон поиска (регулярное выражение)
            attr['column'] =  self._get_range(self._config[f'{doc["name"]}_{i}']['column']) #колонка для поиска данных аттрибут
            attr['row'] =  self._get_range(self._config[f'{doc["name"]}_{i}']['row']) #запись (в области) для поиска данных атрибутта
            doc['attributes'].append(attr)
        self._documents.append(doc)

    @check_error
    def _get_range(self, x:str) -> list:
        return [ int(i) for i in x.split(',')]


