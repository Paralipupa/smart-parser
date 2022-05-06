from typing import NoReturn
from module.excel_base_importer import ExcelBaseImporter
import re


class ReportPU(ExcelBaseImporter):

    def __init__(self, file_name:str, inn:str, config_file:str) -> NoReturn:
        super().__init__(file_name, inn, config_file)

    def process_record(self, team : dict):
        for item_doc in self._config._documents:            
            doc = dict()
            for item_attr  in item_doc['attributes']:
                doc.setdefault(item_attr['name'], list())
                key = self._get_key(item_attr['column'][0])
                row = item_attr['row'][0]
                if key:
                    value = self._get_value(team[key][row], item_attr['pattern'] )
                    if value:
                        doc[item_attr['name']].append(value)
            self._collections.setdefault(item_doc['name'], list())
            self._collections[item_doc['name']].append(doc)

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






