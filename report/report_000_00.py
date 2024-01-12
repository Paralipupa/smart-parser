from module.excel_base_importer import ExcelBaseImporter


class Report_000_00(ExcelBaseImporter):

    def __init__(self, file_name: str, config_file: str, inn: str = ''):
        super().__init__(file_name, config_file, inn)

