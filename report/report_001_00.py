from typing import NoReturn
from module.excel_base_importer import ExcelBaseImporter

##
##   
##
class Report_001_00(ExcelBaseImporter):

    def __init__(self, file_name:str, inn:str, config_file:str) -> NoReturn:
        super().__init__(file_name, inn, config_file)

    def process_record(self, team : dict) -> NoReturn:
        super().process_record(team)















