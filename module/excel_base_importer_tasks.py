import re
import os
import datetime
import pathlib
import uuid
import csv
import json
import logging
from typing import Union
from itertools import product
from .gisconfig import GisConfig
from module.exceptions import InnMismatchException
from .file_readers import get_file_reader
from preliminary.utils import get_ident, get_reg
from .helpers import (
    hashit,
    warning_error,
    fatal_error,
    print_message,
    regular_calc,
    get_value_int,
    get_value_float,
    get_value_range,
    get_months,
    get_absolute_index,
)
from .settings import *

logger = logging.getLogger(__name__)


class ExcelBaseImporter:
    @fatal_error
    def __init__(self, file_name: str, config_file: str, inn: str):
        self.is_file_exists = True
        self.is_hash = True
        self.is_check = False
        self._teams = (
            list()
        )  # список данных сгруппированных по идентификатору - internal_id
        self._dictionary = dict()
        self._columns = dict()
        self._headers = list()
        self.colontitul = {
            "status": 0,
            "is_parameters": False,
            "head": list(),  # до таблицы
            "foot": list(),  # после таблицы
        }  # список  записей вне таблицы
        self._names = dict()  # колонки таблицы
        self._parameters = dict()  # параметры отчета (период, имя_файла, инн и др.)
        self._parameters["inn"] = {
            "fixed": True,
            "value": [inn if inn else "0000000000"],
        }
        self._parameters["filename"] = {"fixed": True, "value": [file_name]}
        self._parameters["config"] = {"fixed": True, "value": [config_file]}
        self._collections = dict()  # коллекция выходных таблиц
        self._config = GisConfig(config_file)
        self._page_index = self._config._page_index[0][POS_NUMERIC_VALUE]
        self._page_name = self._config._page_name
        self.__set_functions()

    # %% Проверка совместимости файла конфигурации
    def check(self, headers: list, is_warning: bool = False) -> bool:
        if not self.is_verify(self._parameters["filename"]["value"][0]):
            return False
        if (
            self._parameters["inn"]["value"][-1] != "0000000000"
            and self._config._parameters.get("inn")
            and self._config._parameters.get("inn")[0]["pattern"][0] != "@inn"
            and not re.search(
                self._parameters["inn"]["value"][-1],
                self._config._parameters.get("inn")[0]["pattern"][0],
            )
        ):
            return False
        self._headers = (
            self.__get_headers()
            if len(headers) < self._config._max_rows_heading[0][0]
            else headers
        )
        if len(headers) < len(self._headers):
            headers.clear()
            headers.extend(self._headers)
        if not self._headers:
            return False
        return self._check_controll(self._headers, is_warning)

    def _check_controll(self, headers: list, is_warning: bool = False) -> list:
        self.is_check = True
        is_check = False if self._config._check["pattern"][0]["pattern"] else True
        for row in range(self._config._max_rows_heading[0][0]):
            if row < len(headers):
                if not is_check:
                    for patt in self._config._check["pattern"]:
                        if not patt["is_find"]:
                            patt["is_find"] = any(
                                [re.search(patt["pattern"], x) for x in headers[row]]
                            )
                    is_check = all(
                        [x["is_find"] for x in self._config._check["pattern"]]
                    )
                names = self.__get_names(headers[row])
                self.__check_columns(names, row)
                if (
                    is_check
                    and self.__check_stable_columns()
                    and self.__check_condition_team(self.__map_record(headers[row]))
                ):
                    self.is_check = False
                    return self.__check_function()
        self.is_check = False
        if self._parameters["inn"]["value"][-1] != "0000000000" and not re.search(
            "000_00", self._config._config_name
        ):
            mess = ""
            x = [
                x["pattern"]
                for x in self.__get_columns_heading()
                if not x["optional"] and not x["active"]
            ]
            if x:
                s = ""
                for patterns in x:
                    for name in patterns:
                        s += "\t" + name + ";\n"
                mess += (
                    "Не найдены обязательные колонки согласно шаблонов:\n{0}".format(s)
                )
            else:
                x = [
                    x["pattern"]
                    for x in self._config._check["pattern"]
                    if x["is_find"] == False
                ]
                if x:
                    mess += (
                        'Не найден текст перед табличными данными:\n\t"{0}"\n'.format(
                            '"\n\t"'.join(x).replace("|", '"\n\t"')
                        )
                    )
                if mess:
                    self._config._warning.append(mess)
        return False

    @fatal_error
    def is_verify(self, file_name: str) -> bool:
        if not self.__is_init():
            return False
        if not os.path.exists(self._parameters["filename"]["value"][0]):
            self._config._warning.append(f"ОШИБКА чтения файла {file_name}")
            self.is_file_exists = False
            return False
        return True

    # %% Точка входа, чтение и обработка файла
    @fatal_error
    def extract(self) -> bool:
        if not self.is_verify(self._parameters["filename"]["value"][0]):
            return False
        if not self.__get_col_start():
            self.__set_col_start(0)
        for col_start in self.__get_col_start():
            self.__init_data()
            self._col_start = col_start[0]
            for page in self.__get_pages():
                self._page_name = (
                    page[POS_PAGE_VALUE]
                    if isinstance(page[POS_PAGE_VALUE], str)
                    else ""
                )
                self._page_index = (
                    page[POS_PAGE_VALUE] if isinstance(page[POS_PAGE_VALUE], int) else 0
                )
                if not self.__get_header("pattern"):
                    self.colontitul["status"] = 1
                data_reader = self.__get_data_xls()
                if not data_reader:
                    self._config._warning.append(
                        f"\nОШИБКА чтения файла {self._parameters['filename']['value'][0]}"
                    )
                    continue
                row = 0
                for record in data_reader:
                    if row < 100 and row % 10 == 0:
                        print_message(
                            "         {} Обработано: {}                          \r".format(
                                self.func_inn(), row
                            ),
                            end="",
                            flush=True,
                        )
                    record = record[self._col_start :]
                    if self.colontitul["status"] != 2:
                        # Область до или после таблицы
                        if not self.__check_bound_row(row):
                            break
                        self.__check_colontitul(self.__get_names(record), row, record)
                    if self.colontitul["status"] == 2:
                        # Табличная область данных
                        self.__check_record_in_body(record, row)
                    row += 1
                    if row % 100 == 0:
                        print_message(
                            "         {} Обработано: {}                          \r".format(
                                self.func_inn(), row
                            ),
                            end="",
                            flush=True,
                        )
                self.__done()
                self._page_index += 1
        self.__process_finish()
        return True

    def __get_pages(self):
        pages = list()
        page_indexes = self.__get_page_index()
        if self.__get_page_name():
            pages = [(x, False) for x in self.__get_page_name().split(",")]
        else:
            pages.append(page_indexes)
        return pages

    # Формируем словарь колонок из записи исходной таблицы
    # key - имя колонки
    # value - словарь
    #   row - порядковый номер строки в группе
    #   col - номер колонки в группе
    #   active - найдена колонка в исходной  таблице или нет
    #  indexes - список номеров колонок в виде кортежа (номер, признак отриц.значения) в исходной таблице откуда берутся данные
    def __map_record(self, record):
        result_record = dict()
        is_empty = True
        for key, value in self._names.items():
            result_record.setdefault(key, [])
            size = len(result_record[key])
            for index in value["indexes"]:
                if index[POS_INDEX_VALUE] in range(len(record)):
                    v = record[index[POS_INDEX_VALUE]]
                    is_empty = is_empty and (v == "" or v is None)
                    result_record[key].append(
                        {
                            "row": size,
                            "col": value["col"],
                            "index": index[POS_INDEX_VALUE],
                            "value": v,
                            "negative": index[POS_INDEX_IS_NEGATIVE],
                        }
                    )
        return result_record if not is_empty else None

    # группируем записи по идентификатору
    def __append_to_team(self, mapped_record: list) -> bool:
        if self.__check_condition_team(mapped_record):
            # запись относится к текущему идентификатору
            self._teams.append(mapped_record)
            return True
        elif len(self._teams) != 0:
            for key in mapped_record.keys():
                size = self._teams[-1][key][-1]["row"] + 1
                for mr in mapped_record[key]:
                    self._teams[-1][key].append(
                        {
                            "row": size,
                            "col": mr["col"],
                            "index": mr["index"],
                            "value": mr["value"],
                            "negative": mr["negative"],
                        }
                    )
        return False

    # Проверяем условие завершения группировки записей по текущему идентификатору
    def __check_condition_team(self, mapped_record: list) -> bool:
        if not self.__get_condition_team():
            return True
        if not mapped_record:
            return False
        b = False
        for p in self.__get_condition_team():
            if mapped_record.get(p["col"]):
                for patt in p["pattern"]:
                    result = self.__get_condition_data(mapped_record[p["col"]], patt)
                    b = False if not result or result.find("error") != -1 else True
                    if b:
                        if len(self._teams) != 0:
                            # Проверяем значение со значением из предыдущей области (иерархии)
                            # если не совпадает, то фиксируем начало новой области (иерархии)
                            pred = self.__get_condition_data(
                                self._teams[-1][p["col"]], patt
                            )
                            b = result != pred
                        if b:
                            return b
        return b

    # Область до или после таблицы
    def __check_bound_row(self, row: int) -> bool:
        if self.__get_row_start() + self.__get_max_rows_heading() < row:
            if len(self._teams) != 0:
                return False
            s1, s2, is_active_find = "", "", False
            for item in self.__get_columns_heading():
                if not item["active"]:
                    if not item["optional"]:
                        s1 += f"{item['name']} {'не обязат.' if item['optional'] else ''},\n"
                        is_active_find = True
                else:
                    c = ""
                    for index in item["indexes"]:
                        c += f"({item['row']},{index[POS_INDEX_VALUE]}) "
                    s2 += f"{item['name']} {c}\n"

            if is_active_find:
                self._config._warning.append(
                    '\n{}:\nВ загружаемом файле "{}"\nне все колонки найдены \n'.format(
                        self._config._config_name,
                        self._parameters["filename"]["value"][0],
                    )
                )
                if s2:
                    self._config._warning.append(
                        "Найдены колонки:\n{}\n".format(s2.strip())
                    )
                if s1:
                    self._config._warning.append(
                        "Не найдены колонки:\n{}\n".format(s1.strip())
                    )
            else:
                s = "Найдены колонки:"
                for key, value in self._names.items():
                    s += f"\n{key} - {value['indexes'][0][POS_INDEX_VALUE]}"
                self._config._warning.append(
                    '\n{0}:\nВ загружаемом файле "{1}" \
                \nне верен шаблон нахождения начала области данных(({3})condition_begin_team(\n{2}\n))\n{4}\n'.format(
                        self._config._config_name,
                        self._parameters["filename"]["value"][0],
                        self.__get_condition_team()[0]["pattern"]
                        if self.__get_condition_team()
                        else "",
                        self.__get_condition_team()[0]["col"]
                        if self.__get_condition_team()
                        else "",
                        s,
                    )
                )

            return False
        return True

    def __check_colontitul(self, names: list, row: int, record: list):
        if self.colontitul["status"] == 0:
            if self.__check_headers_status(names):
                if len(self._teams) != 0:
                    self.__process_record(self._teams[-1])
                    self.__init_data()
                    self.__set_row_start(row)
        if self.__check_columns(names, row):
            self._row_start = row
        if self.colontitul["status"] == 1:
            if self.__check_stable_columns():
                if (
                    len(self.__get_columns_heading()) <= len(self._names)
                ) or self.__check_condition_team(self.__map_record(record)):
                    # переход в табличную область данных
                    self.colontitul["status"] = 2
                    self.__dynamic_change_config()
                    self._config._parameters.setdefault(
                        "table_start",
                        [
                            {
                                "row": [row],
                                "col": [0],
                                "pattern": [f"@{row}"],
                                "ishead": True,
                            }
                        ],
                    )

    # Проверка записи в таблице
    def __check_record_in_body(self, record: list, row: int):
        if self._config._rows_exclude:
            # если номер записи в исключении, то пропускаем его
            if row in [
                x[0] + self._config._parameters["table_start"][0]["row"][0]
                for x in self._config._rows_exclude
            ]:
                if self.colontitul["head"] and self.colontitul["head"][-1] != record:
                    self.colontitul["head"].append(record)
                return
        mapped_record = self.__map_record(record)
        if mapped_record:  # строка не пустая
            if self.__check_end_table(mapped_record):
                # достигнут конец таблицы
                self.colontitul["status"] = 0
                self.colontitul["is_parameters"] = False
                self.__set_row_start(row)
                for item in self.__get_columns_heading():
                    item["active"] = False
                self.colontitul["foot"].append(record)
            elif self.__append_to_team(mapped_record):  # если добавлена новая группа
                # если уже нашли более одной группы, то добавляем предпоследнюю в документ
                if len(self._teams) > 1:
                    self.__process_record(self._teams[-2])
        if len(self._teams) < 2:
            # добавляем первые записи в таблице в область заголовка
            # (иногда там могут находиться некоторые параметры)
            self.colontitul["head"].append(record)

    def __check_columns(self, names: list, row: int) -> bool:
        is_find = False
        if names:
            last_cols = []
            # список уже добавленных колонок, которые нужно исключить при следующем прохождении
            cols_exclude = list()
            for x in [x["indexes"] for x in self._names.values()]:
                cols_exclude.extend([y[POS_INDEX_VALUE] for y in x])
            # сначала проверяем обязательные и приоритетные колонки
            for item in self.__get_columns_heading():
                if (
                    (not item["active"] or item["duplicate"])
                    and item["pattern"][0]
                    and (not item["optional"] or item["priority"])
                ):
                    if self.__check_column(item, names, row, cols_exclude):
                        is_find = True
            # потом проверяем остальные колонки
            for item in self.__get_columns_heading():
                if (
                    (not item["active"] or item["duplicate"])
                    and item["pattern"][0]
                    and item["optional"]
                    and not item["priority"]
                ):
                    if item["after_stable"]:
                        last_cols.append(item)
                    elif self.__check_column(item, names, row, cols_exclude):
                        is_find = True
            # последние колонки (after_stable = True) Прочие услуги
            for item in last_cols:
                if self.__check_stable_columns() and (
                    row in self.__get_rows_header() or item["duplicate"]
                ):
                    if self.__check_column(item, names, row, cols_exclude, True):
                        is_find = True
        return is_find

    def __check_column(
        self,
        item: dict,
        names: list,
        row: int,
        cols_exclude: list = [],
        is_last: bool = False,
    ) -> dict:
        is_find = False
        patt = ""
        for p in item["pattern"]:
            patt = patt + ("|" if patt else "") + p
        search_names = self.__get_search_names(
            names, patt, item, cols_exclude if not item["duplicate"] else []
        )  # колонки в таблице Excel
        if search_names:
            for search_name in search_names:
                col_left = self.__get_border(item, "left", search_name["col"])
                col_right = self.__get_border(item, "right", search_name["col"])
                if col_left <= search_name["col"] <= col_right:
                    key = item["name"]
                    self._names.setdefault(
                        key,
                        {"row": row, "col": item["col"], "active": True, "indexes": []},
                    )
                    self._names[key]["active"] = True
                    item["active"] = True if not item["after_stable"] else False
                    if item["col_data"]:
                        for val in item["col_data"]:
                            index = get_absolute_index(val, search_name["col"])
                            # добавляем номер колонки из исходной таблицы для суммирования значений
                            # задается параметром "col_data_offset" в настройках
                            if not (
                                (index, val[POS_NUMERIC_IS_NEGATIVE])
                                in self._names[key]["indexes"]
                            ):
                                item["indexes"].append(
                                    (index, val[POS_NUMERIC_IS_NEGATIVE])
                                )
                                self._names[key]["indexes"].append(
                                    (index, val[POS_NUMERIC_IS_NEGATIVE])
                                )
                    else:
                        if not (
                            (search_name["col"], False) in self._names[key]["indexes"]
                        ):
                            item["indexes"].append((search_name["col"], False))
                            self._names[key]["indexes"].append(
                                (search_name["col"], False)
                            )
                            if is_last:
                                self._columns[search_name["col"]] = search_name["name"]
                    item["row"] = row
                    is_find = True
                    if not is_last:
                        cols_exclude.append(search_name["col"])
                    else:
                        for x in cols_exclude:
                            while self._names[key]["indexes"].count((x, False)) > 0:
                                self._names[key]["indexes"].remove((x, False))
                                item["indexes"].remove((x, False))
                                self._columns.pop(x)
                    if item["unique"]:
                        break
        return is_find

    # Проверка на наличие всех обязательных колонок
    def __check_stable_columns(self) -> bool:
        return all(
            [x["active"] for x in self.__get_columns_heading() if not x["optional"]]
        )

    # Проверка на наличие 'якоря' (текста, смещенного относительно позиции текущего заголовка)
    # параметры offset_col, offset_row, offsert_pattern в разделах [col_X]
    def __check_column_offset(self, item: dict, index: int) -> bool:
        offset = item["offset"]
        if offset and offset["pattern"][0]:
            rows = [i for i in offset["row"]]
            if not rows:
                rows = [(0, False)]
            cols = offset["col"]
            if not cols:
                cols = [(i, True) for i in range(len(self.colontitul["head"][-1]))]
            row_count = len(self.colontitul["head"])
            col_left = self.__get_border(item, "left", 0)
            col_right = self.__get_border(item, "right", index)
            if col_left <= index <= col_right:
                for row, col in product(rows, cols):
                    r = get_absolute_index(row, row_count - 1)
                    c = get_absolute_index(col, index)
                    if (
                        not (r == 0 and c == 0)
                        and 0 <= r < len(self.colontitul["head"])
                        and 0 <= c < len(self.colontitul["head"][r])
                    ):
                        result = regular_calc(
                            offset["pattern"][0], self.colontitul["head"][r][c]
                        )
                        if result != None:
                            return True
            return False
        return True

    def __check_end_table(self, mapped_record) -> bool:
        if not self.__get_condition_end_table():
            return False
        result = regular_calc(
            self.__get_condition_end_table(),
            mapped_record[self.__get_condition_end_table_column()][0]["value"],
        )
        if result != None:
            return True
        return False

    def __check_period_value(self):
        patts = [
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%y",
            "%d.%m.%y",
            "%d/%m/%y",
            "%B %Y",
        ]
        d = None
        for item in self._parameters["period"]["value"]:
            if item:
                for p in patts:
                    try:
                        d = datetime.datetime.strptime(item, p)
                        break
                    except:
                        pass
        ls = list()
        if d:
            ls.append(d.date().replace(day=1).strftime("%d.%m.%Y"))
            ls.append(d.date().strftime("%d.%m.%Y"))
        else:
            result = regular_calc("19[89][0-9]|20[0-3][0-9]", item)
            if result != None:
                year = result
                month = next(
                    (
                        val
                        for key, val in get_months().items()
                        if re.search(key + r"[а-я]{0,5}\s", item, re.IGNORECASE)
                    ),
                    None,
                )
                if month:
                    ls.append(f"01.{month}.{year}")
                else:
                    ls.append(datetime.date.today().strftime("%d.%m.%Y"))
        self._parameters["period"]["value"] = list()
        if ls:
            for item in ls:
                self._parameters["period"]["value"].append(item)
        else:
            self._parameters["period"]["value"].append(
                datetime.date.today().replace(day=1).strftime("%d.%m.%Y")
            )

    def __check_headers_status(self, names):
        if self.colontitul["status"] == 1:
            return False
        m = self.__get_header("pattern")
        if not m:
            self.colontitul["status"] = 1
        else:
            if self.__get_search_names(names, m):
                self.colontitul["status"] = 1
        return self.colontitul["status"] == 1

    @warning_error
    def __get_condition_data(self, values: list, pattern: str) -> str:
        result = ""
        for val in values:
            if val["row"] == 0:
                patt = pattern.split("|")[0] if result == "" else pattern
                value = regular_calc(patt, val["value"])
                if value == None:
                    if result == "":
                        return ""
                else:
                    result += value
        return result

    def __get_data_xls(self):
        ReaderClass = get_file_reader(self._parameters["filename"]["value"][0])
        data_reader = ReaderClass(
            self._parameters["filename"]["value"][0],
            self._page_name,
            0,
            range(self._col_start + self.__get_max_cols()),
            self._page_index,
        )
        if not data_reader:
            self.is_file_exists = False
            self._config._warning.append(
                f"\nОШИБКА чтения файла {self._parameters['filename']['value'][0]}"
            )
            return None
        return data_reader

    def __get_border(self, item: dict, name: str, col: int = 0) -> int:
        if item[name]:
            name_field = self.__get_key_from_input_names(
                item[name][0][POS_NUMERIC_VALUE]
            )
            if name_field:
                col = self._names[name_field]["indexes"][0][POS_INDEX_VALUE]
            else:
                col = col + 1 if name == "left" else col - 1
        return col

    def __get_rows_header(self) -> set:
        return {x["row"] for x in self._names.values()}

    def _get_check_pattern(self) -> list:
        rows: list[int] = self.__get_check("row")  # раздел [check]
        if not rows:
            rows.append((0, False))
        patts = list()
        p = self.__get_check("pattern")  # раздел [check]
        patts.append(
            {"pattern": p, "full": True, "find": p == "", "maxrow": rows[-1][0]}
        )
        i = 0
        p = self.__get_check(f"pattern_{i}")  # раздел [check]
        while p:
            p = self.__get_check(f"pattern_{i}")
            patts.append(
                {"pattern": p, "full": True, "find": False, "maxrow": rows[-1][0]}
            )
            i += 1
            p = self.__get_check(f"pattern_{i}")

        # разделы [col_]
        for item in self._config._columns_heading:
            s = ""
            for patt in item["pattern"]:
                s += patt + "|"
            s = s.strip("|")
            patts.append(
                {
                    "pattern": s,
                    "full": False,
                    "find": item["optional"] or not s,
                    "maxrow": self._config._max_rows_heading[0][0],
                }
            )
        return patts

    def __get_headers(self) -> list:
        self._col_start = 0
        data_reader = self.__get_data_xls()
        if not data_reader:
            return None
        headers = list()
        index = 0
        for record in data_reader:
            headers.append(record)
            index += 1
            if index > self._config._max_rows_heading[0][0]:
                break
        return headers

    def __check_function(self) -> bool:
        f = self._config._check["func"]
        if not f:
            return True
        patt = [self._config._check["func_pattern"]]
        item_fld = {
            "func": f,
            "func_pattern": patt,
            "is_offset": False,
            "type": "",
            "offset_type": "",
            "value": "",
            "value_o": "",
        }
        value = self.func(team=dict(), fld_param=item_fld, row=0, col=0)
        return True if value else False

    def __get_value_after_validation(
        self, pattern: str, name: str, row: int, col: int
    ) -> str:
        try:
            if (
                row < len(self.colontitul[name])
                and col < len(self.colontitul[name][row])
                and self.colontitul[name][row][col]
            ):
                result = regular_calc(pattern, self.colontitul[name][row][col])
                if result != None:
                    return result
                else:
                    return ""
            else:
                return ""
        except Exception as ex:
            logger.exception("Ошибка получения данных")
            return f"error: {ex}"

    def __get_names(self, record: list) -> dict:
        names = []
        index = 0
        if (self.colontitul["status"] == 1) or (
            self.colontitul["status"] == 0 and len(self._names) == 0
        ):
            self.colontitul["head"].append(record)
        elif self.colontitul["status"] == 0 and len(self._names) > 0:
            self.colontitul["foot"].append(record)
        for cell in record:
            # if cell:
            nm = dict()
            nm["name"] = str(cell).strip()
            nm["col"] = index
            nm["active"] = False
            names.append(nm)
            index += 1
        return names

    def __get_search_names(
        self, names: list, pattern: str, item: list = [], cols_exclude: list = []
    ) -> list:
        results = []
        for name in names:
            if not (name["col"] in cols_exclude):
                result = regular_calc(f"{pattern}", name["name"])
                if result != None:
                    b = True
                    if item and item.get("offset") and item["offset"]["pattern"][0]:
                        b = self.__check_column_offset(item, name["col"])
                    if b:
                        results.append(name)
        return results

    def __get_key_from_input_names(self, col: int) -> str:
        for key, value in self._names.items():
            if value["col"] == col:
                return key
        return ""

    def __get_value(
        self, value: str = "", pattern: str = "", type_value: str = ""
    ) -> Union[str, int, float]:
        try:
            value = str(value)
            if type_value == "int":
                value = str(get_value_int(value))
            elif type_value == "double" or type_value == "float":
                value = str(get_value_float(value))
        except:
            pass
        result = regular_calc(pattern, value)
        if result != None:
            try:
                if type_value == "int":
                    result = get_value_int(value)
                elif type_value == "double" or type_value == "float":
                    result = get_value_float(result)
                else:
                    result = result.rstrip() + " "
            except:
                result = 0
        else:
            if type_value == "int":
                result = 0
            elif type_value == "double" or type_value == "float":
                result = 0
            else:
                result = ""
        return result

    def __get_doc_param_fld(self, name: str, fld_name: str):
        doc = next(
            (x for x in self.__get_config_documents() if x["name"] == name), None
        )
        if doc:
            fld = next((x for x in doc["fields"] if x["name"] == fld_name), None)
            return fld
        return None

    def __get_fld_records(self, item_fld: dict):
        records = list()
        records.append(item_fld.copy())
        records[-1]["value"] = (
            0 if records[-1]["type"] == "float" or records[-1]["type"] == "int" else ""
        )
        records[-1]["value_o"] = (
            0
            if (
                records[-1]["offset_type"] == "float"
                or records[-1]["offset_type"] == "int"
            )
            else ""
        )
        for sub in item_fld["sub"]:
            records.append(sub.copy())
            records[-1]["value"] = (
                0
                if records[-1]["type"] == "float" or records[-1]["type"] == "int"
                else ""
            )
            records[-1]["value_o"] = (
                0
                if (
                    records[-1]["offset_type"] == "float"
                    or records[-1]["offset_type"] == "int"
                )
                else ""
            )
        return records

    def __get_total_value_from_values(
        self, values: list, type_fld: str, pattern: str
    ) -> str:
        value = self.__get_value(type_value=type_fld)
        for val in values:
            if (type_fld == "int" or type_fld == "float") and val[
                POS_NUMERIC_IS_NEGATIVE
            ]:
                value -= self.__get_value(val[POS_VALUE], pattern, type_fld)
            else:
                try:
                    value += self.__get_value(val[POS_VALUE], pattern, type_fld)
                except Exception as ex:
                    pass
        if not (type_fld == "float" or type_fld == "double" or type_fld == "int"):
            value = value.lstrip()
        return value

    # данные из колонки по смещению (offset_column_)
    def __get_value_from_offset(
        self, team: dict, record: dict, row_curr: int, col_curr: int
    ) -> Union[str, int, float]:
        rows: list = record["offset_row"]
        cols: list = record["offset_column"]
        value: str = record["value_o"]
        if not rows:
            rows = [(0, False)]
        if not cols:
            cols = [(col_curr, True)]
        for c in cols:
            fld_name = self.__get_key_from_input_names(c[POS_NUMERIC_VALUE])
            if fld_name:
                row = get_absolute_index(rows[0], row_curr)
                values = [
                    (x["value"], None, x["negative"] | c[POS_NUMERIC_IS_NEGATIVE])
                    for x in team[fld_name]
                    if x["row"] == row
                ]
                x = self.__get_total_value_from_values(
                    values=values,
                    type_fld=record["offset_type"],
                    pattern=record["offset_pattern"][0],
                )
                value += x if not isinstance(x, str) or value.find(x) == -1 else ""
        return value

    def __get_required_rows(self, name: str, doc: dict) -> set:
        s = set()
        d = next((x for x in self.__get_config_documents() if x["name"] == name), None)
        if d and d["required_fields"]:
            for name_field in d["required_fields"].split(","):
                fld_type = next(
                    (
                        x["type"] + x["offset_type"]
                        for x in d["fields"]
                        if x["name"] == name_field
                    ),
                    "",
                )
                for item in doc[name_field]:
                    val = self.__get_value(str(item["value"]), ".+", fld_type)
                    if (
                        (fld_type == "" or fld_type == "str") and val.strip() != ""
                    ) or ((fld_type == "float" or fld_type == "int") and val != 0):
                        s.add(item["row"])
        return s

    def __is_data_depends(
        self, record: dict, doc: dict, doc_param: dict
    ) -> Union[str, bool]:
        if not record["depends"]:
            return True
        fld = record["depends"]
        if doc[fld] and doc[fld][0]["value"]:
            fld_param = self.__get_doc_param_fld(doc_param["name"], fld)
            x = self.__get_value(
                doc[fld][0]["value"], ".+", fld_param["type"] + fld_param["offset_type"]
            )
        else:
            x = ""
        return x

    def __done(self):
        if len(self._teams) != 0:
            self.__process_record(self._teams[-1])

    def __process_record(self, team: dict) -> None:
        if not self.colontitul["is_parameters"]:
            self.__set_parameters()
        for doc_param in self.__get_config_documents():
            doc = self.__set_document(team, doc_param)
            self.__document_split_one_line(doc, doc_param)
        self._teams.remove(team)

    def __process_finish(self) -> None:
        for doc_param in self.__get_config_documents():
            if doc_param.get("func_after"):
                param = {"value": "", "func": doc_param["func_after"]}
                self.func(
                    fld_param=param, team=self._collections.get(doc_param["name"])
                )

    # %%Изменение конфигурации "на ходу"
    def __dynamic_change_config(self):
        self.__change_heading()
        self.__change_pp()

    # Добавляем услуги, отсутствующие в конфигурации, но имеющиеся в заголовках таблицы
    def __change_pp(self):
        if len(self._columns) == 0:
            return
        docs = [
            x
            for x in self._config._documents
            if x["name"] in ("pp_charges", "pp_service")
        ]
        for doc in docs:
            flds = [
                x
                for x in doc["fields"]
                if x["name"]
                in (
                    "internal_id",
                    "pp_internal_id",
                    "calc_value",
                    "tariff",
                    "service_internal_id",
                    "recalculation",
                    "accounting_period_total",
                    "name",
                    "kind",
                )
            ]
            for fld in flds:
                if fld["sub"]:
                    ls = []
                    for key, name in self._columns.items():
                        ls.append(fld["sub"][-1].copy())
                        ls[-1]["func"] = ls[-1]["func"].replace(
                            "Прочие", name.replace(",", " ")
                        )
                        if len(fld["sub"][-1]["offset_column"]) > 0:
                            l = [
                                x
                                for x in self._config._columns_heading
                                if x["name"] == get_ident(name)
                            ]
                            if l:
                                ls[-1]["offset_column"] = [(l[0]["col"], True, False)]
                    fld["sub"][-1]["offset_column"] = [(-1, True, False)]
                    fld["sub"].extend(ls)

    # Добавляем колонки, отсутствующие в конфигурации, но имеющиеся в заголовках таблицы
    def __change_heading(self):
        for key, name in self._columns.items():
            l = self._config._columns_heading[-1].copy()
            l["name"] = get_ident(name)
            l["pattern"] = [get_reg(name)]
            l["indexes"] = [(key, False)]
            l["col"] = len(self._config._columns_heading)
            l["after_stable"] = False
            l["duplicate"] = False
            l["activate"] = True
            self._config._columns_heading.append(l)
            self._names[l["name"]] = {
                "row": l["row"],
                "col": l["col"],
                "active": True,
                "indexes": l["indexes"],
            }

    # если текущая таблица типа словарь, то формируем глобальный словарь значений
    # для последующих таблиц
    def __build_global_dictionary(self, doc: dict):
        param = {}
        for key, value in doc.items():
            if key == "key":
                param = {"value": doc["key"], "func": "hash"}
                param["key"] = self.func(fld_param=param)
            elif re.search("^value", key):
                param["data"] = value
            else:
                self._dictionary.setdefault(self.__get_index_key(key), [])
                if not value in self._dictionary[self.__get_index_key(key)]:
                    self._dictionary[self.__get_index_key(key)].append(value)
            if param.get("key") and param.get("data"):
                self._dictionary.setdefault(self.__get_index_key(param["key"]), [])
                if (
                    not param["data"]
                    in self._dictionary[self.__get_index_key(param["key"])]
                ):
                    self._dictionary[self.__get_index_key(param["key"])].append(
                        param["data"]
                    )

    #%%##############################################################################################################################################
    # --------------------------------------------------- Документы --------------------------------------------------------------------------------
    ################################################################################################################################################
    def __append_to_collection(self, name: str, doc: dict) -> None:
        key = self._page_name if self._page_name else "noname"
        self._collections.setdefault(name, {key: list()})
        self._collections[name].setdefault(key, list())
        self._collections[name][key].append(doc)
        if (
            self.__get_doc_type(name) == "dictionary"
            and doc.get("key")
            and doc.get("value")
        ):
            self.__build_global_dictionary(doc)

    # Формирование документа из части исходной таблицы - team (отдельной области или иерархии)
    # выбранной по идентификатору internal_id
    def __set_document(self, team: dict, doc_param):
        doc = dict()
        for fld_item in doc_param["fields"]:  # перебор полей выходной таблицы
            # Формируем данные для записи в выходном файле
            # одно поле (ключ в doc) соответствует одной записи
            doc.setdefault(fld_item["name"], list())
            main_rows_exclude = (
                set()
            )  # набор записей для исключение по основному значению
            offset_rows_exclude = set()  # набор записей для исключение по смещению
            for table_row in doc_param["rows_exclude"]:
                main_rows_exclude.add((table_row[0], -1))
            # собираем все поля (sub): name_attr, name_attr_0, ... , name_attr_N
            fld_records = self.__get_fld_records(fld_item)
            for fld_record in fld_records:
                if (
                    not fld_record["column"]
                    or not fld_record["pattern"]
                    or not fld_record["pattern"][0]
                ):
                    continue
                col = fld_record["column"][0]
                name_field = self.__get_key_from_input_names(col[POS_VALUE])
                if not name_field:
                    continue
                for table_row in fld_record["rows_exclude"]:
                    main_rows_exclude.add((table_row[0], -1))
                table_rows = get_value_range(fld_record["row"], len(team[name_field]))
                for table_row in table_rows:  # обрабатываем все строки области данных
                    if (
                        len(team[name_field]) > table_row[0]
                        and not (table_row[0], -1) in main_rows_exclude
                        and not (table_row[POS_VALUE], col[POS_VALUE])
                        in main_rows_exclude
                    ):
                        for patt in fld_record["pattern"]:
                            # Берем данные из исходной таблицы
                            values = [
                                (
                                    x["value"],
                                    col[POS_NUMERIC_IS_ABSOLUTE],
                                    col[POS_NUMERIC_IS_NEGATIVE],
                                )
                                for x in team[name_field]
                                if x["row"] == table_row[POS_VALUE]
                            ]
                            # И получаем из них одно значение
                            x = self.__get_total_value_from_values(
                                values=values, type_fld=fld_record["type"], pattern=patt
                            )
                            if x:
                                fld_record["value"] += (
                                    x
                                    if not isinstance(x, str)
                                    or fld_record["value"].find(x) == -1
                                    else ""
                                )
                                if fld_record["is_offset"]:
                                    if (
                                        not (
                                            table_row[POS_VALUE],
                                            col[POS_VALUE],
                                            fld_record["offset_column"][0][POS_VALUE],
                                        )
                                        in offset_rows_exclude
                                    ):
                                        # если есть смещение по таблице относительно текущего значения,
                                        # то берем данные от туда
                                        fld_record[
                                            "value_o"
                                        ] = self.__get_value_from_offset(
                                            team,
                                            fld_record,
                                            table_row[0],
                                            col[POS_VALUE],
                                        )
                                        # запоминаем, чтобы не было повтора
                                        offset_rows_exclude.add(
                                            (
                                                table_row[POS_VALUE],
                                                col[POS_VALUE],
                                                fld_record["offset_column"][0][
                                                    POS_VALUE
                                                ],
                                            )
                                        )
                                else:
                                    # запоминаем, чтобы не было повтора
                                    main_rows_exclude.add(
                                        (table_row[0], col[POS_VALUE])
                                    )
                                break  # пропускаем проверку по остальным шаблонам
                if fld_record["func"]:
                    # если есть, запускаем функцию
                    fld_record["value"] = self.func(
                        team=team, fld_param=fld_record, row=table_row[0], col=col[0]
                    )
                elif fld_record["is_offset"]:
                    fld_record["value"] = fld_record["value_o"]
                    fld_record["type"] = fld_record["offset_type"]
                if fld_record["value"] and not self.__is_data_depends(
                    fld_record, doc, doc_param
                ):
                    # Если поле зависит от значения другого поля и это значение пусто,
                    # то текущее значение тоже обнуляем (наприме, дату если соответствующая сумма = 0 )
                    fld_record["value"] = ""
                # формируем документ
                doc[fld_record["name"]].append(
                    {
                        "row": len(doc[fld_record["name"]]),
                        "col": col[0],
                        "value": ""
                        if (
                            (
                                isinstance(fld_record["value"], int)
                                or isinstance(fld_record["value"], float)
                            )
                            and fld_record["value"] == 0
                        )
                        or (
                            isinstance(fld_record["value"], str)
                            and fld_record["offset_type"] == "float"
                            and fld_record["value"] == "0.0"
                        )
                        else str(fld_record["value"]).strip(),
                    }
                )
        return doc

    # Разбиваем данные документа по-строчно
    def __document_split_one_line(self, doc: dict, doc_param: dict) -> None:
        name = doc_param["name"]
        # для каждого поля свой индекс прохода
        index = {x: 0 for x in doc.keys()}
        rows = [x[-1]["row"] for x in doc.values() if x]
        counts = [len(x) for x in doc.values() if x]
        rows = rows + counts
        rows_count = max(rows) if rows else 0
        rows_required = self.__get_required_rows(name, doc)
        rows_exclude = [
            x[0] if x[0] >= 0 else rows_count + 1 + x[0]
            for x in doc_param["rows_exclude"]
        ]
        i = -1
        done = True

        while done:
            i += 1
            done = i < rows_count
            elem = dict()
            is_empty = True
            for key, values in doc.items():
                elem[key] = ""
                if index[key] < len(values):
                    # проверяем соответствие номера строки (row) в данных с номером записи (i) в выходном файле
                    if values[index[key]]["row"] == i:
                        elem[key] = values[index[key]]["value"]
                        is_empty = is_empty and (values[index[key]]["value"] == "")
                        index[key] += 1
                        done = True
                    elif values[0]["row"] == 0:
                        elem[key] = values[0]["value"]
                elif len(values) == 1 and values[0]["row"] == 0:
                    elem[key] = values[0]["value"]
            if (
                not is_empty
                and not (i in rows_exclude)
                and (not doc_param["required_fields"] or i in rows_required)
            ):
                self.__append_to_collection(name, elem)

    ################################################################################################################################################
    # --------------------------------------------------- Запись в файл ----------------------------------------------------------------------------
    ################################################################################################################################################
    def write_collections(
        self, num: int = 0, path_output: str = "output", output_format: str = ""
    ) -> None:
        if not self.__is_init() or len(self._collections) == 0:
            logger.warning(
                'Не удалось прочитать данные из файла "{0} - {1}"\n'.format(
                    self.func_inn(), self._parameters["filename"]["value"][0]
                )
            )
            return

        os.makedirs(path_output, exist_ok=True)

        self._current_id = ""
        id = self.func_id()
        inn = self.func_inn()
        for name, pages in self._collections.items():
            for key, records in pages.items():
                file_output = pathlib.Path(
                    path_output,
                    f'{inn}{"_"+str(num) if num != 0 else ""}'
                    + f'{"_"+key.replace(" ","_") if key != "noname" else ""}{id}_{name}',
                )
                if not output_format or output_format == "json":
                    with open(
                        f"{file_output}.json", mode="w", encoding=ENCONING
                    ) as file:
                        jstr = json.dumps(records, indent=4, ensure_ascii=False)
                        file.write(jstr)

                if not output_format or output_format == "csv":
                    with open(
                        f"{file_output}.csv", mode="w", encoding=ENCONING
                    ) as file:
                        names = [x for x in records[0].keys()]
                        file_writer = csv.DictWriter(
                            file, delimiter=";", lineterminator="\r", fieldnames=names
                        )
                        file_writer.writeheader()
                        for rec in records:
                            file_writer.writerow(rec)

    def write_logs(self, num: int = 0, path_output: str = "logs") -> None:
        if not self.__is_init() or len(self._collections) == 0:
            return
        os.makedirs(path_output, exist_ok=True)
        self._current_id = ""
        id = self.func_id()
        inn = self.func_inn()
        i = 0
        file_output = pathlib.Path(
            path_output, f'{inn}{"_"+str(num) if num != 0 else ""}{id}'
        )
        with open(f"{file_output}.log", "w", encoding=ENCONING) as file:
            file.write(f"{{")
            for key, value in self._parameters.items():
                file.write(f'\t{key}:"')
                for index in value["value"]:
                    file.write(f"{index} ")
                file.write(f'",\n')
            file.write(f"}},\n")
            file.write(f"\n{{")
            for item in self._config._columns_heading:
                if item["row"] != -1:
                    file.write(
                        f"\t({item['col']}){item['name']}:  row={item['row']} col="
                    )
                    for index in item["indexes"]:
                        file.write(f"{index[POS_INDEX_VALUE]},")
                    file.write(f'",\n')
            file.write(f"}},\n\n")
            file.write("\nself._parameters\n")
            jstr = json.dumps(self._parameters, indent=4, ensure_ascii=False)
            file.write(jstr)
            file.write("\nself._config._parameters\n")
            jstr = json.dumps(self._config._parameters, indent=4)
            file.write(jstr)
            file.write("\nself._config._columns_heading\n")
            jstr = json.dumps(
                self._config._columns_heading, indent=4, ensure_ascii=False
            )
            file.write(jstr)

    ################################################################################################################################################
    # ---------------------------------------------- Параметры конфигурации ------------------------------------------------------------------------
    ################################################################################################################################################
    def __set_parameters(self) -> None:
        for value in self._parameters.values():
            if not value["fixed"]:
                value["value"] = list()
        for key in self.__get_config_parameters().keys():
            self.__set_parameter(key)
        self._parameters.setdefault("period", {"fixed": False, "value": list()})

        if not self._parameters["period"]["value"]:
            self._parameters["period"]["value"].append(
                datetime.date.today().strftime("%d.%m.%Y")
            )
        self.__check_period_value()

        self._parameters.setdefault("path", {"fixed": False, "value": list()})
        if not self._parameters["path"]["value"]:
            self._parameters["path"]["value"].append(PATH_OUTPUT)
        self._parameters.setdefault("address", {"fixed": False, "value": list()})
        if not self._parameters["address"]["value"]:
            self._parameters["address"]["value"].append("")
        self.colontitul["is_parameters"] = True
        if self._parameters["inn"]["value"][
            0
        ] != "0000000000" and self._config._parameters.get("inn"):
            l = [
                x
                for x in self._config._parameters["inn"]
                if x["pattern"][0].find(self._parameters["inn"]["value"][0]) != -1
            ]
            if not l:
                raise InnMismatchException

    def __set_parameter(self, name: str):
        for param in self.__get_config_parameters(name):
            rows = param["row"]
            cols = param["col"]
            patterns = param["pattern"]
            is_head = param["ishead"]
            func = param.get("func")
            self._parameters.setdefault(name, {"fixed": False, "value": list()})
            if func:
                value = self.func(fld_param={"func": func})
                if value:
                    self._parameters[name]["value"].append(value)
            else:
                for pattern in patterns:
                    if pattern:
                        if pattern[0] == "@":
                            self._parameters[name]["value"].append(pattern[1:])
                        else:
                            for row, col in product(rows, cols):
                                result = self.__get_value_after_validation(
                                    pattern,
                                    "head" if is_head else "foot",
                                    row[0],
                                    col[0],
                                )
                                if result:
                                    if param["offset_pattern"]:
                                        if not param["offset_row"]:
                                            param["offset_row"].append((0, False))
                                        if not param["offset_col"]:
                                            param["offset_col"].append((0, False))
                                        result = self.__get_value_after_validation(
                                            param["offset_pattern"],
                                            "head" if is_head else "foot",
                                            get_absolute_index(
                                                param["offset_row"][0], row[0]
                                            ),
                                            get_absolute_index(
                                                param["offset_col"][0], col[0]
                                            ),
                                        )
                                    if result:
                                        self._parameters[name]["value"].append(
                                            param["value"]
                                            if param.get("value")
                                            else result
                                        )
                                        break

        return self._parameters[name]

    def __is_init(self) -> bool:
        return self._config._is_init

    def __get_columns_heading(self, col: int = -1, name: str = "") -> list:
        if col != -1:
            if name:
                return self._config._columns_heading[col][name]
            else:
                return self._config._columns_heading[col]
        else:
            return self._config._columns_heading

    def __get_condition_team(self) -> str:
        return self._config._condition_team

    def __get_condition_end_table(self) -> str:
        return self._config._condition_end_table

    def __get_doc_type(self, name: str) -> str:
        return "".join(
            [x["type"] for x in self._config._documents if x["name"] == name]
        )

    def __get_condition_end_table_column(self) -> str:
        return self._config._condition_end_table_column

    def __get_page_name(self) -> str:
        return self._config._page_name

    def __get_page_index(self) -> int:
        return get_value_int(self._config._page_index)

    def __get_max_cols(self) -> int:
        return get_value_int(self._config._max_cols)[0]

    def __get_row_start(self) -> int:
        return get_value_int(self._config._row_start)[0]

    def __get_col_start(self) -> int:
        return self._config._col_start

    def __set_col_start(self, col: int):
        self._config._col_start.append((col, True))

    def __set_row_start(self, row: int):
        self._config._row_start = [(row, True)]

    def __get_max_rows_heading(self) -> int:
        return get_value_int(self._config._max_rows_heading)[0]

    def __get_header(self, name: str):
        return self._config._header[name]

    @warning_error
    def __get_check(self, name: str):
        return self._config._check[name]

    def __get_config_parameters(self, name: str = ""):
        if name:
            return self._config._parameters[name]
        else:
            return self._config._parameters

    def __get_config_documents(self, name: str = ""):
        if name:
            return self._config._documents[name]
        else:
            return self._config._documents

    def __init_data(self):
        self.colontitul["head"] = list()
        if self.colontitul["foot"]:
            self.colontitul["head"].append(self.colontitul["foot"][-1])
        self.colontitul["foot"] = list()
        for col in self.__get_columns_heading():
            col["active"] = False
        self._names = dict()
        self._teams = list()

    ################################################################################################################################################
    # ----------------------------------------------------- Функции --------------------------------------------------------------------------------
    ################################################################################################################################################
    def __set_functions(self) -> None:
        self.funcs = {
            "inn": self.func_inn,
            "period_first": self.func_period_first,
            "period_last": self.func_period_last,
            "period_month": self.func_period_month,
            "period_year": self.func_period_year,
            "column_name": self.func_column_name,
            "account_number": self.func_account_number,
            "bik": self.func_bik,
            "column_value": self.func_column_value,
            "hash": self.func_hash,
            "guid": self.func_uuid,
            "param": self.func_param,
            "spacerem": self.func_spacerem,
            "spacerepl": self.func_spacerepl,
            "round2": self.func_round2,
            "round4": self.func_round4,
            "round6": self.func_round6,
            "opposite": self.func_opposite,
            "param": self.func_param,
            "dictionary": self.func_dictionary,
            "to_date": self.func_to_date,
            "id": self.func_id,
            "check_bank_accounts": self.func_bank_accounts,
        }
        self._current_value = list()
        self._current_id = ""

    def __get_index_find_any(self, text: str, delimeters: str) -> int:
        a = []
        for item in delimeters:
            index = text.find(item)
            if index != -1:
                a.append(index)
        return min(a) if a else -1

    def __get_index_key(self, line: str) -> str:
        return re.sub("[-.,() ]", "", line).lower()

    def __get_func_list(self, part: str, names: str):
        self._current_value_func.setdefault(part, {})
        list_sub = re.findall(r"[a-z_0-9]+\(.+\)", names)
        for item in list_sub:
            ind_s = item.find("(")
            ind_e = item.find(")")
            func = item[:ind_s]
            arg = item[ind_s + 1 : ind_e]
            hash = hashit(func.encode("utf-8"))[:8]
            if not self._current_value_func[part].get(hash):
                self._current_value_func[part][hash] = {
                    "name": func,
                    "type": "sub",
                    "input": "",
                    "output": "",
                }
                arg_hash = self.__get_func_list(hash, arg)
                self._current_value_func[hash]["expression"] = arg_hash
                names = names.replace(item, hash)
        names_new = ""
        while True:
            index = self.__get_index_find_any(names, "+-,")
            delim = ""
            if index == -1:
                item = names
                names = ""
            else:
                item = names[:index]
                delim = names[index : index + 1]
                names = names[index + 1 :]
            hash = hashit(item.encode("utf-8"))[:8]
            self._current_value_func[part][hash] = {
                "name": item,
                "type": "",
                "input": "",
                "output": "",
            }
            names_new += f"{hash}{delim}"
            if not names:
                break
        return names_new

    def __recalc_expression(self, part: str) -> None:
        for item in self._current_value_func[part]["expression"].split(","):
            value = self._current_value_empty
            for index, hash in enumerate(re.split(r"[+-]", item)):
                self._current_index = 0
                name = self._current_value_func[part][hash]["name"]
                if re.search(r"(?<=\[)\d(?=\])", name):
                    self._current_index = int(re.findall(r"(?<=\[)\d(?=\])", name)[0])
                    name = re.findall(r".+(?=\[)", name)[0]
                if self._current_value_func[part].get(name):
                    self._current_value.append(value)
                    ind = self._current_index
                    self.__recalc_expression(name)
                    self._current_index = ind
                    name = self._current_value_func[part][name]["name"]
                if self.funcs.get(name.strip()):
                    f = self.funcs.get(name.strip())
                    x = f()
                    if isinstance(value, float) or isinstance(value, int):
                        if item.find(f"-{name}") != -1 and index != 0:
                            value -= self.__get_value(x, ".+", "float")
                        else:
                            value += self.__get_value(x, ".+", "float")
                    else:
                        value += x + " "
                else:
                    if self._dictionary.get(self.__get_index_key(name)):
                        value = (
                            value.strip()
                            + self._dictionary[self.__get_index_key(name)][0]
                        )
                    elif self._parameters.get(name):
                        value = value.strip() + (
                            self._parameters[name]["value"][-1]
                            if len(self._parameters[name]["value"]) > 0
                            else ""
                        )
                    elif name == "_":
                        value = (
                            value.strip()
                            + (" " if value else "")
                            + self._current_value[-1]
                        )
                    else:
                        if isinstance(value, str):
                            value = value.strip() + (" " if value else "") + name
                        else:
                            pass
                if self._current_value_func[part].get(
                    self._current_value_func[part][hash]["name"]
                ):
                    self._current_value.pop()
            self._current_value.pop()
            self._current_value.append(
                value.rstrip() if isinstance(value, str) else value
            )

    def func(
        self, team: dict = {}, fld_param: dict = {}, row: int = 0, col: int = 0
    ) -> str:
        self._current_id = fld_param.get("value", "")
        self._current_index = 0
        self._current_value = list()
        if fld_param.get("is_offset"):
            value = fld_param.get("value_o", "")
            self._current_value_type = fld_param.get("offset_type", "str")
        else:
            value = fld_param.get("value", "")
            self._current_value_type = fld_param.get("type", "str")
        self._current_value_pattern = (
            fld_param["func_pattern"][0] if fld_param.get("func_pattern") else ""
        )
        self._current_value_empty = 0 if self._current_value_type == "float" else ""
        self._current_value_team = team
        self._current_value_row = row
        self._current_value_col = col
        self._current_value_param = fld_param
        self._current_value_func_is_no_return = fld_param.get(
            "func_is_no_return", False
        )
        self._current_value_func = {}
        part = "00000000"
        m = fld_param.get("func", "")
        m = self.__get_func_list(part, m)
        self._current_value_func[part]["expression"] = m
        self._current_value.append(value)
        self.__recalc_expression(part)
        value = self._current_value.pop()
        if self._current_value_func_is_no_return and str(value).strip():
            for x in [
                x
                for x in re.split(r"[+-,]", fld_param.get("func", ""))
                if re.search("^[a-z_0-9]+$", x)
            ]:
                if str(value).find(x) != -1:
                    value = ""
                    break
        return str(value).strip()

    def func_inn(self):
        if self._parameters["inn"]["value"][0] != "0000000000":
            return self._parameters["inn"]["value"][0]
        else:
            return self._parameters["inn"]["value"][-1]

    def func_period_first(self):
        period = datetime.datetime.strptime(
            self._parameters["period"]["value"][-1], "%d.%m.%Y"
        )
        return period.replace(day=1).strftime("%d.%m.%Y")

    def func_period_last(self):
        period = datetime.datetime.strptime(
            self._parameters["period"]["value"][-1], "%d.%m.%Y"
        )
        next_month = period.replace(day=28) + datetime.timedelta(days=4)
        return (next_month - datetime.timedelta(days=next_month.day)).strftime(
            "%d.%m.%Y"
        )

    def func_period_month(self):
        return self._parameters["period"]["value"][0][3:5]

    def func_period_year(self):
        return self._parameters["period"]["value"][0][6:]

    def func_to_date(self):
        patts = [
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%y",
            "%d.%m.%y",
            "%d/%m/%y",
            "%B %Y",
        ]
        for p in patts:
            try:
                d = datetime.datetime.strptime(self._current_value[-1], p)
                return self._current_value[-1]
            except:
                pass
        return ""

    def func_hash(self):
        return (
            hashit(str(self.__get_index_key(self._current_value[-1])).encode("utf-8"))
            if self.is_hash
            else self._current_value[-1]
        )

    def func_uuid(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self._current_value[-1]))

    def func_id(self):
        d = self._parameters["period"]["value"][0]
        return f"{str(self._current_id).strip()}_{d[3:5]}{d[6:]}"  # _mmyyyy

    def func_column_name(self):

        if self._current_value_col != -1:
            return self.__get_columns_heading(self._current_value_, "alias")
        return ""

    def func_column_value(self):
        value = next(
            (
                x[self._current_value_row]["value"]
                for x in self._current_value_team.values()
                if x[self._current_value_row]["col"] == int(self._current_value[-1])
            ),
            "",
        )
        return value

    def func_param(self):
        m = ""
        for item in self._parameters[self._current_value[-1]]["value"]:
            m += (item.strip() + " ") if isinstance(item, str) else ""
        return f"{m.strip()}"

    def func_spacerem(self):
        return self._current_value[-1].strip().replace(" ", "")

    def func_spacerepl(self):
        return self._current_value[-1].strip().replace(" ", "_")

    def func_round2(self):
        return (
            str(round(self._current_value[-1], 2))
            if isinstance(self._current_value[-1], float)
            else str(self._current_value[-1])
        )

    def func_round4(self):
        return (
            str(round(self._current_value[-1], 4))
            if isinstance(self._current_value[-1], float)
            else self._current_value[-1]
        )

    def func_round6(self):
        return (
            str(round(self._current_value[-1], 6))
            if isinstance(self._current_value[-1], float)
            else self._current_value[-1]
        )

    def func_opposite(self):
        return (
            str(-self._current_value)
            if isinstance(self._current_value, float)
            else self._current_value
        )

    def func_account_number(self):
        pattern = re.compile(REG_KP_XLS)
        if self._dictionary.get("account_number"):
            if pattern.search(self._parameters["filename"]["value"][0].lower()):
                return (
                    self._dictionary.get("account_number", [])[-1]
                    if len(self._dictionary.get("account_number", [])) != 0
                    else ""
                )
            else:
                return (
                    self._dictionary.get("account_number", [])[0]
                    if len(self._dictionary.get("account_number", [])) != 0
                    else ""
                )
        elif self._parameters.get("account_number"):
            if pattern.search(self._parameters["filename"]["value"][0].lower()):
                return (
                    self._parameters.get("account_number", {"value": [""]})["value"][-1]
                    if len(
                        self._parameters.get("account_number", {"value": [""]})["value"]
                    )
                    != 0
                    else ""
                )
            else:
                return (
                    self._parameters.get("account_number", {"value": [""]})["value"][0]
                    if len(
                        self._parameters.get("account_number", {"value": [""]})["value"]
                    )
                    != 0
                    else ""
                )
        else:
            return ""

    def func_bik(self):
        pattern = re.compile(REG_KP_XLS)
        if self._dictionary.get("bik"):
            if pattern.search(self._parameters["filename"]["value"][0].lower()):
                return (
                    self._dictionary.get("bik", [])[-1]
                    if len(self._dictionary.get("bik", [])) != 0
                    else ""
                )
            else:
                return (
                    self._dictionary.get("bik", [])[0]
                    if len(self._dictionary.get("bik", [])) != 0
                    else ""
                )
        elif self._parameters.get("bik"):
            if pattern.search(self._parameters["filename"]["value"][0].lower()):
                return (
                    self._parameters.get("bik", {"value": [""]})["value"][-1]
                    if len(self._parameters.get("bik", {"value": [""]})["value"]) != 0
                    else ""
                )
            else:
                return (
                    self._parameters.get("bik", {"value": [""]})["value"][0]
                    if len(self._parameters.get("bik", {"value": [""]})["value"]) != 0
                    else ""
                )
        else:
            return ""

    def func_dictionary(self):
        return (
            self._dictionary.get(self.__get_index_key(self._current_value[-1]), [])[
                self._current_index
            ]
            if len(
                self._dictionary.get(self.__get_index_key(self._current_value[-1]), [])
            )
            > self._current_index
            else self._dictionary.get(
                self.__get_index_key(self._current_value[-1]), []
            )[-1]
            if len(
                self._dictionary.get(self.__get_index_key(self._current_value[-1]), [])
            )
            > 0
            else ""
        )

    def func_bank_accounts(self):
        if not self._current_value_team:
            return ""
        d = {}
        u = {}
        exist_overhaul = False
        for item in self._current_value_team["noname"]:
            d.setdefault(item.get("internal_id"), item)
        for item in d.values():
            if item.get("is_overhaul"):
                exist_overhaul = True
            u.setdefault(item["account_number"], 0)
            u[item["account_number"]] += 1
        if exist_overhaul == False:
            mess = 'В тарифах отсутствует колонка "Кап.ремонт"'
            self._config._warning.append(mess)
        if [x for x in u.values() if x > 1]:
            mess = "Конфликт в расчетном счете по капитальному ремонту"
            self._config._warning.append(mess)
        return ""
