from typing import NoReturn
from module.excel_base_importer import ExcelBaseImporter

##
##   
##
class Report_002_00(ExcelBaseImporter):

    def __init__(self, file_name:str, config_file:str, inn:str='') -> NoReturn:
        super().__init__(file_name, config_file, inn)

# # Формирование документа из полученной порции (отдельной области или иерархии)
#     def set_document(self, team: dict, doc_param):
#         doc = dict()
#         for item_fld in doc_param['fields']:  # перебор полей выходной таблицы
#             doc.setdefault(item_fld['name'], list())
#             # колонки, данные из которых заполняют поле.
#             # Каждая колонка создает отдельную запись
#             cols = self.get_value_range(item_fld['column'])
#             for col in cols:
#                 name_field = self.get_key(col[0])
#                 if name_field and item_fld['pattern'][0]:
#                     rows = self.get_value_range(
#                         item_fld['row'], len(team[name_field]))
#                     value = self.get_value(type_value=item_fld['type'])
#                     value_off = self.get_value(
#                         type_value=item_fld['offset_type'])
#                     for row in rows:
#                         if len(team[name_field]) > row[0]:
#                             for patt in item_fld['pattern']:
#                                 value += self.get_fld_value(
#                                     team=team[name_field], type_fld=item_fld['type'],
#                                     pattern=patt, row=row[0])
#                                 if not value:
#                                     # если значение пустое, то проверяем под-поля (col_x_y если они заданы)
#                                     value = self.get_sub_value(
#                                         item_fld, team, name_field, row[0], col[0], value)
#                                 else:
#                                     if item_fld['offset_row'] or item_fld['offset_column']:
#                                         # если есть смещение, то берем данные от туда
#                                         value_off += self.get_value_offset(
#                                             team, item_fld, item_fld['offset_type'], row[0], col[0], value_off, len(doc[item_fld['name']]))
#                                     if (value or value_off) and item_fld['func']:
#                                         # запускаем функцию и передаем в нее полученное значение
#                                         if item_fld['offset_row'] or item_fld['offset_column']:
#                                             value_off = self.func(
#                                                 team=team, fld_param=item_fld, data=value_off, row=row[0], col=col[0])
#                                         else:
#                                             value = self.func(
#                                                 team=team, fld_param=item_fld, data=value, row=row[0], col=col[0])
#                                 if value_off or value:
#                                     break
                                    
#                     if value_off or value:
#                         # формируем документ
#                         if (item_fld['offset_row'] or item_fld['offset_column']):
#                             value = value_off
#                         depends = item_fld['depends']
#                         if depends:
#                             if doc[depends] and doc[depends][0]['value']:
#                                 fld_param = self.get_doc_param_fld(doc_param['name'], depends)
#                                 x = self.get_value(doc[depends][0]['value'], '.+', fld_param['type'] + fld_param['offset_type'])
#                             else:
#                                 x = ''
#                             if not x:
#                                 value = ''
#                         if value:
#                             fld_param = self.get_doc_param_fld(doc_param['name'], item_fld['name'])
#                             x = self.get_value(value, '.+', fld_param['type'] + fld_param['offset_type'])
#                             if not x:
#                                 value = ''
#                         if value:
#                             doc[item_fld['name']].append(
#                                 {'row': len(doc[item_fld['name']]), 'col': col[0], 'value': ''
#                                 if (isinstance(value, int) or isinstance(value, float)) and value == 0 else str(value)})
#                 else:
#                     # все равно заносим в документ чтобы не сбивать порядок записей
#                     doc[item_fld['name']].append(
#                         {'row': len(doc[item_fld['name']]), 'col': col[0], 'value': ''})
#         return doc














