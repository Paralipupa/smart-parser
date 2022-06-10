from typing import NoReturn
from module.excel_base_importer import ExcelBaseImporter

##
##
##


class Report_001_00(ExcelBaseImporter):

    def __init__(self, file_name: str, config_file: str, inn: str = '', data=None) -> NoReturn:
        super().__init__(file_name, config_file, inn, data)

# # Формирование документа из полученной порции (отдельной области или иерархии)
#     def set_document(self, team: dict, doc_param):
#         doc = dict()
#         for item_fld in doc_param['fields']:  # перебор полей выходной таблицы
#             doc.setdefault(item_fld['name'], list())
#             # Формируем записи в выходном файле
#             records = self.get_data_records(item_fld)
#             for record in records:
#                 if not record['column'] or not record['pattern'] or not record['pattern'][0]:
#                     continue
#                 col = record['column'][0]
#                 name_field = self.get_key(col[0])
#                 if not name_field:
#                     continue
#                 rows = self.get_value_range(
#                     record['row'], len(team[name_field]))
#                 for row in rows:  # обрабатываем все строки области данных
#                     if len(team[name_field]) > row[0]:
#                         for patt in record['pattern']:
#                             x = self.get_fld_value(
#                                 team=team[name_field],
#                                 type_fld=record['type'],
#                                 pattern=patt, row=row[0])
#                             if x:
#                                 record['value'] += x
#                                 if record['is_offset']:
#                                     # если есть смещение, то берем данные от туда
#                                     record['value_o'] = self.get_value_offset(
#                                         team, record, row[0], col[0])
#                                 break #пропускаем проверку по остальным шаблонам
#                 if record['is_offset']:
#                     record['value'] = record['value_o']
#                 if record['func']:
#                     # запускаем функцию и передаем в нее полученное значение
#                     record['value'] = self.func(
#                         team=team, fld_param=record, data=record['value'], row=row[0], col=col[0])
#                 if record['value'] and not self.is_data_depends(record, doc, doc_param):
#                     record['value'] = ''

#                 # формируем документ
#                 doc[record['name']].append(
#                     {'row': len(doc[record['name']]), 'col': col[0], 'value': ''
#                      if (isinstance(record['value'], int) or isinstance(record['value'], float))
#                      and record['value'] == 0 else str(record['value'])})
#         return doc

#     def is_data_depends(self, record, doc, doc_param):
#         if not record['depends']:
#             return True
#         fld = record['depends']
#         if doc[fld] and doc[fld][0]['value']:
#             fld_param = self.get_doc_param_fld(
#                 doc_param['name'], fld)
#             x = self.get_value(
#                 doc[fld][0]['value'], '.+', fld_param['type'] + fld_param['offset_type'])
#         else:
#             x = ''
#         return x

#     def get_data_records(self, item_fld):
#         records = list()
#         records.append(item_fld.copy())
#         records[-1]['value'] = 0 if records[-1]['type'] == 'float' or records[-1]['type'] == 'int' else ''
#         records[-1]['value_o'] = 0 if (
#             records[-1]['offset_type'] == 'float' or records[-1]['offset_type'] == 'int') else ''
#         for sub in item_fld['sub']:
#             records.append(sub.copy())
#             records[-1]['value'] = 0 if records[-1]['type'] == 'float' or records[-1]['type'] == 'int' else ''
#             records[-1]['value_o'] = 0 if (
#                 records[-1]['offset_type'] == 'float' or records[-1]['offset_type'] == 'int') else ''
#         return records

#     def get_fld_value(self, team: dict, type_fld: str, pattern: str, row: int) -> str:
#         value = self.get_value(type_value=type_fld)
#         for val_item in team:
#             if val_item['row'] == row:
#                 value += self.get_value(
#                     val_item['value'], pattern, type_fld)
#         if (type_fld == 'float' or type_fld == 'double' or type_fld == 'int'):
#             if value == 0:
#                 value = 0
#             else:
#                 value = round(value, 2) if isinstance(
#                     value, float) else value
#         return value

#     # если есть смещение, то берем данные от туда
#     def get_value_offset(self, team, record, row_curr, col_curr):
#         rows = record['offset_row']
#         cols = record['offset_column']
#         value = record['value_o']
#         if not rows:
#             rows = [(0, False)]
#         if not cols:
#             cols = [(col_curr, True)]
#         fld_name = self.get_key(cols[0][0])
#         if fld_name:
#             value += self.get_fld_value(
#                 team=team[fld_name],
#                 type_fld=record['offset_type'],
#                 pattern=record['offset_pattern'][0],
#                 row=rows[0][0]+row_curr if not rows[0][1] else rows[0][0]
#             )
#         return value
