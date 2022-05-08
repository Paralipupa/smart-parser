from typing import NoReturn, Union
from module.excel_base_importer import ExcelBaseImporter

##
##   Данные по приборам учета
##
class Report_001_00(ExcelBaseImporter):

    def __init__(self, file_name:str, inn:str, config_file:str) -> NoReturn:
        super().__init__(file_name, inn, config_file)

class Report_001_00(ExcelBaseImporter):

    def __init__(self, file_name:str, inn:str, config_file:str) -> NoReturn:
        super().__init__(file_name, inn, config_file)

    def process_record(self, team : dict) -> NoReturn:
        for doc_param in self._config._documents:
            doc,count = self.get_document(team, doc_param)
            self.document_split_one_line(doc, count, doc_param['name'])















