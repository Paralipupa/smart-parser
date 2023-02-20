from typing import NoReturn
from module.excel_base_importer import ExcelBaseImporter

##
##   
##
class Report_003_00(ExcelBaseImporter):

    def __init__(self, file_name:str, config_file:str, inn:str='') -> NoReturn:
        super().__init__(file_name, config_file, inn)


