from typing import NoReturn
from module.excel_base_importer import ExcelBaseImporter
import re

##
##   Данные по приборам учета
##
class Report_001_00(ExcelBaseImporter):

    def __init__(self, file_name:str, inn:str, config_file:str) -> NoReturn:
        super().__init__(file_name, inn, config_file)

    def process_record(self, team : dict) -> NoReturn:
        for item_doc in self._config._documents:
            doc = dict()
            count = 0
            for item_attr  in item_doc['attributes']:
                doc.setdefault(item_attr['name'], list())
                key = self._get_key(item_attr['column'][0])
                if key and item_attr['pattern']:
                    if item_attr['row'] == '*':
                        rows = range(len(team[key]))
                    else:
                        rows = item_attr['row']
                    for row in rows:
                        if len(team[key]) > row and team[key][row]:
                            value = self._get_value(team[key][row], item_attr['pattern'] )
                            if value:
                                doc[item_attr['name']].append(value)
                                count = len(doc[item_attr['name']]) if len(doc[item_attr['name']]) > count else count
            self._collections.setdefault(item_doc['name'], list())
            for i in range(count):
                elem = dict()
                for key, value in doc.items():
                    elem[key] = list()
                    if i < len(value):
                        elem[key].append(value[i])
                    elif len(value) != 0:
                        elem[key].append(value[0])
                self._collections[item_doc['name']].append(elem)

    def _get_key(self, index:int) -> str:
        for key, value in self._names.items():
            if value['index'] == index:
                return key
        return ''

    def _get_value(self, value:str, pattern:str) -> str:
        result = re.search(pattern, value)
        if result:
            return result.group(0)
        return ''






