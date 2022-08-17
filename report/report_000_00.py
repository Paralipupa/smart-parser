# from typing import NoReturn
# from module.excel_base_importer import ExcelBaseImporter

# class Report_001_00(ExcelBaseImporter):

#     def __init__(self, file_name: str, config_file: str, inn: str = '', data=None) -> NoReturn:
#         super().__init__(file_name, config_file, inn, data)

#     def set_document(self, team: dict, doc_param):
#         doc = dict()
#         for item_fld in doc_param['fields']:  # перебор полей выходной таблицы
#             doc.setdefault(item_fld['name'], list())
#             # колонки, данные из которых заполняют поле.
#             # Каждая колонка создает отдельную запись
#             cols = self._get_value_range(item_fld['column'])
#             for col in cols:
#                 name_field = self._get_key(col[0])
#                 if name_field and item_fld['pattern'][0]:
#                     rows = self._get_value_range(
#                         item_fld['row'], len(team[name_field]))
#                     for row in rows:
#                         if len(team[name_field]) > row[0]:
#                             for patt in item_fld['pattern']:
#                                 value = self._get_fld_value(
#                                     team=team[name_field], type_fld=item_fld['type'],
#                                     pattern=patt, row=row[0])
#                                 if not value:
#                                     # если значение пустое, то проверяем под-поля (col_x_y если они заданы)
#                                     value = self.get_sub_value(
#                                         item_fld, team, name_field, row[0], col[0], value)
#                                 else:
#                                     if item_fld['offset_row'] or item_fld['offset_column']:
#                                         # если есть смещение, то берем данные от туда
#                                         value = self._get_value_offset(
#                                             team, item_fld, item_fld['offset_type'], row[0], col[0], '')
#                                     if value and item_fld['func']:
#                                         # запускаем функцию и передаем в нее полученное значение
#                                         value = self.func(
#                                             team=team, fld_param=item_fld, data=value, row=row[0], col=col[0])
#                                 if value:
#                                     # формируем документ
#                                     doc[item_fld['name']].append(
#                                         {'row': len(doc[item_fld['name']]), 'col': col[0], 'value': value})
#                                     break
#                 else:
#                     # все равно заносим в документ
#                     doc[item_fld['name']].append(
#                         {'row': len(doc[item_fld['name']]), 'col': col[0], 'value': ''})
#         return doc

#     # если есть смещение, то берем данные от туда
#     # rank = кол-во сформированных записей для данной области в выходном файле
#     # если в смещение задается несколько колонок (Report_002), то выбираем
#     # значение в соответствии с порядковым номером записи.
#     def _get_value_offset(self, team, item_fld, item_type, row_curr, col_curr, value, rank: int = 0):
#         rows = item_fld['offset_row']
#         cols = item_fld['offset_column']
#         if not rows:
#             rows = [(0, False)]
#         if not cols:
#             cols = [(col_curr, False)]
#         if len(cols) == 1:
#             rank = 0  # если задано только одно значение смещения, то выбираем первую выходную запись
#         if rank < len(cols):
#             col = cols[rank]
#             for r in rows:
#                 m_key = self._get_key(col[0])
#                 if m_key:
#                     value = self._get_fld_value(
#                         team=team[m_key], type_fld=item_fld['offset_type'], pattern=item_fld['offset_pattern'][0],
#                         row=r[0]+row_curr if not r[1] else r[0]
#                     )
#         return value


#     def _get_fld_value(self, team: dict, type_fld: str, pattern: str, row: int) -> str:
#         value = self._get_value(type_value=type_fld)
#         for val_item in team:
#             if val_item['row'] == row:
#                 value += self._get_value(
#                     val_item['value'], pattern, type_fld)
#         if (type_fld == 'float' or type_fld == 'double' or type_fld == 'int'):
#             if value == 0:
#                 value = 0
#             else:
#                 value = round(value, 2) if isinstance(
#                     value, float) else value
#         return value

