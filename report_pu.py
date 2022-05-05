from typing import NoReturn
from excel_base_importer import ExcelBaseImporter 


class ReportPU(ExcelBaseImporter):

    def __init__(self, config_file:str) -> NoReturn:
        super().__init__(config_file)

    def process_record(self, is_last : bool = False):
        if len(self._documents) == 0:
            return
        elif is_last:
            document = self._documents[-1]
        elif len(self._documents) > 1:
            document = self._documents[-2]
        else:
            return
        
        

        
