from typing import NoReturn
from excel_base_importer import ExcelBaseImporter


class ReportPU(ExcelBaseImporter):

    def __init__(self, config_file:str) -> NoReturn:
        super().__init__(config_file)

    def process_record(self, is_last : bool = False):
        if len(self._team) == 0:
            return
        elif is_last:
            section = self._team[-1]
        elif len(self._team) > 1:
            section = self._team[-2]
        else:
            return
            
        documents = list()
        for key, value in section.items():
            pass





