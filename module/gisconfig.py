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
            return None
    return wrapper

class GisConfig:

    def __init__(self, filename : str):
        self._is_init = False
        if self.is_exist(filename):
            self._config = configparser.ConfigParser()
            self._config.read(filename)
            self.configuration_initialize()

    def is_exist(self, filename : str) -> bool:
        return os.path.exists(filename)

    @check_error
    def configuration_initialize(self) -> NoReturn:
        self._condition_team:str = ''  #условие начала новой области (регулярное выражение)
        self._condition_column:int = '' # колонка в которой просматривается условие области
        self._columns_heading:list[str] = []  # список заголовков колонок таблицы 
        self._columns_heading_offset:list[dict] = [] #список "якорей" заголовков таблицы 
        self._row_start:int = self.read_config('main','row_start',isNumeric=True)    #
        self._page_name:str = self.read_config('main','page_name')         #
        self._page_index:int = self.read_config('main','page_index',isNumeric=True)  #
        self._max_cols:int = self.read_config('main','max_columns',isNumeric=True)   #максимальное кол-во просматриваемых колонок 
        self._max_rows_heading:int = self.read_config('main','max_rows_heading',isNumeric=True) #максимальное кол-во строк до таблицы
        self._documents:list[dict] = [] #список документов (настроек)
        self._parameters = dict()

        self.set_parameters()

        num_cols = self.read_config('main','columns_count',isNumeric=True)
        self._columns_heading = [self.read_config(f'col_{i}','pattern') for i in range(num_cols[0])]
        for i in range(num_cols[0]):
            self.set_conditions(i)
            self.set_heading_offset(i)

        num_cols = self.read_config('main','documents_count',isNumeric=True)
        for i in range(num_cols[0]):
            self.set_documents(i)
            
        self._is_init = True

    @check_error
    def set_parameters(self):
        self._parameters['period'] = {'row':0, 'col':0, 'pattern':''}
        self._parameters['path'] = self.read_config('main','path')
        num_parms = self.read_config('main','parameters_count',isNumeric=True)
        for i in range(num_parms[0]):
            self._parameters[self.read_config(f'param_{i}','name')] = {
                'row' : self.read_config(f'param_{i}','row',isNumeric=True),
                'col' : self.read_config(f'param_{i}','column',isNumeric=True),
                'pattern' : self.read_config(f'param_{i}','pattern'),
            }

    def set_conditions(self, i:int) -> NoReturn:
        if not self._condition_team:
            self._condition_team = self.read_config(f'col_{i}','condition_team')
            self._condition_column = self.read_config(f'col_{i}','pattern')

    def set_heading_offset(self, i:int):
        off = {'row':[0], 'col':[0], 'text':'', 'is_include':False}
        self._columns_heading_offset.append(off)
        self._columns_heading_offset[-1]['row'] = self.read_config(f'col_{i}','row_offset',isNumeric=True)
        self._columns_heading_offset[-1]['col'] = self.read_config(f'col_{i}','col_offset',isNumeric=True)
        self._columns_heading_offset[-1]['text'] = self.read_config(f'col_{i}','pattern_offset')
        self._columns_heading_offset[-1]['is_include'] = False if self.read_config(f'col_{i}','is_include_offset')=='0' \
            else True
    
    @check_error
    def set_documents(self, i:int) -> NoReturn:
        doc = dict()
        doc['name'] = self.read_config(f'doc_{i}','name')
        doc['fields'] = list()
        num_docs = self.read_config(f'doc_{i}','fields_count',isNumeric=True)
        for i in range(num_docs[0]):
            fld = dict()
            fld['name'] = self.read_config(f'{doc["name"]}_{i}','name') #имя аттрибута
            fld['pattern'] =  self.read_config(f'{doc["name"]}_{i}','pattern') #шаблон поиска (регулярное выражение)
            fld['column'] =  self.read_config(f'{doc["name"]}_{i}','col_config',isNumeric=True) #колонка для поиска данных аттрибут
            fld['row'] =  self.read_config(f'{doc["name"]}_{i}','row_data',isNumeric=True) #запись (в области) для поиска данных атрибутта
            fld['func'] =  self.read_config(f'{doc["name"]}_{i}','func') #запись (в области) для поиска данных атрибутта
            doc['fields'].append(fld)
        self._documents.append(doc)
    
    @check_error
    def get_range(self, x:str) -> list:
        return [ int(i) for i in x.split(',')]

    def read_config(self, name_section:str, name_param:str, isNumeric:bool=False):
        try:
            result:str = self._config[name_section][name_param]
            if isNumeric:
                if result.find(',') != -1:
                    return self.get_range(result)
                elif result:
                    return [int(result)]
                else:
                    return []
            return result
        except:
            if isNumeric:
                return []
            else:
                return ''

