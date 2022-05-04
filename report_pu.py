from typing import NoReturn
from excel_base_importer import ExcelBaseImporter 


class ReportPU(ExcelBaseImporter):

    def __init__(self, file_name : str, inn : str) -> NoReturn:
        super().__init__(max_cols=20, page_index=0, page_name=None, collection=None,
                        cleanup_table=True)
        self.filename = file_name
        self.inn = inn

    # def process_record(self, mapped_record):
    #     reg = self.get_condition_range()
    #     is_bound = False
    #     for value in mapped_record.values():
    #         match = re.search(reg, value[0]) 
    #         if match:
    #             is_bound = True
    #             break
    #     if is_bound or len(self.collections) == 0:
    #         self.collections.append(mapped_record)
    #     else:
    #         for key, value in mapped_record.items():
    #             self.collections[-1][key].append(value[0])

