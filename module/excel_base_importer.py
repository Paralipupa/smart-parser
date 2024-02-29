import re
import os
import datetime
import pathlib
import uuid
import csv
import aiofiles
import asyncio
import json
import logging
from functools import partial
from multiprocessing import Pool, Manager
from multiprocessing.managers import DictProxy
from threading import Thread, Event, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from collections import OrderedDict
from aiocsv import AsyncWriter, AsyncDictWriter
from typing import Union, List
from itertools import product
from .gisconfig import GisConfig
from module.exceptions import InnMismatchException
from .file_readers import get_file_reader
from preliminary.utils import get_ident, get_reg
from module.func import Func
from .helpers import (
    write_log_time,
    warning_error,
    fatal_error,
    print_message,
    regular_calc,
    get_value,
    get_value_int,
    get_value_range,
    get_months,
    get_absolute_index,
    get_index_key,
)
from .settings import *

# manager = Manager()
# man: DictProxy = manager.dict()
# man.collections = dict()
logger = logging.getLogger(__name__)


class ExcelBaseImporter:
    @fatal_error
    def __init__(
        self,
        file_name: str,
        config_files: list,
        inn: str,
        index: int = 0,
        output: str = "output",
        period: datetime.date = None,
        is_hash: bool = True,
        dictionary: dict = dict(),
        download_file: str = "",
    ):
        self.num_file = index
        self.index_config: int = 0
        self.config_files = config_files
        self._output = output
        self.is_file_exists = True
        self.is_hash = is_hash
        self.is_check_mode = False
        self.is_condition_check = False
        self._period = period
        self._dictionary = dictionary
        self.download_file = download_file
        # список данных, сгруппированных по идентификатору - internal_id
        self.colontitul = {
            "status": 0,
            "is_parameters": False,
            "head": list(),  # до таблицы
            "foot": list(),  # после таблицы
        }  # список  записей вне таблицы

        self._teams = (
            OrderedDict()
        )  # блоки данных из таблицы сгруппированных по идентификатору (internal_id)
        self._collections = dict()  # коллекция выходных документов
        self._possible_columns = dict()
        self._headers = list()
        self._column_names = dict()
        self._parameters = dict()  # параметры отчета (период, имя_файла, инн и др.)
        self._parameters["inn"] = {
            "fixed": True,
            "value": [inn if inn else "0000000000"],
        }
        self._parameters["filename"] = {"fixed": True, "value": [file_name]}
        self._column_names = dict()  # колонки таблицы
        self.ex = Event()
        self.lock = Lock()
        self.row = 0
        self.Func: Func = Func(
            self._parameters, self._dictionary, self._column_names, self.is_hash
        )
        self.func = self.Func.func
        self.func_id = self.Func.func_id
        self.func_inn = self.Func.func_inn
        self.__init_page()

    ###################  Проверка совместимости файла конфигурации ######################
    def check(self, sheets_in: list, is_warning: bool = False) -> bool:
        self.__init_config()
        self.__read_config()
        is_find = False
        if not self.is_verify(self._parameters["filename"]["value"][0]):
            mess = f'Файл не найден {self._parameters["filename"]["value"][0]}'
            self.__add_warning(mess)
            logger.warning(mess)
            return False
        if self.__check_incorrect_inn():
            mess = f"\tНе прошла проверка по ИНН "
            self.__add_warning(mess)
            # logger.warning(mess)
            return False
        if sheets_in:
            sheets = sheets_in.copy()
        else:
            sheets = self.__get_headers()
        for index, rows in enumerate(sheets):
            self.__init_data()
            self.__init_page()
            if self.__check_controll(rows, True):
                self.config_files[self.index_config - 1]["sheets"].append(index)
                is_find = True
        mess = f'\t{os.path.basename(self.config_files[self.index_config-1]["name"])}'
        if not sheets_in:
            for sheet in sheets:
                sheets_in.append(sheet)
        # logger.debug(mess)
        return is_find

    @fatal_error
    def is_verify(self, file_name: str) -> bool:
        if not self.__is_init():
            return False
        if not os.path.exists(self._parameters["filename"]["value"][0]):
            self.__add_warning(f"ОШИБКА чтения файла {file_name}")
            self.is_file_exists = False
            return False
        return True

    ####################  Точка входа, чтение и обработка файла #############################
    @fatal_error
    def extract(self) -> bool:
        try:
            data_reader = self.__get_data_xls()
            if not data_reader:
                self.__add_warning(
                    f"\nОШИБКА чтения файла {self._parameters['filename']['value'][0]}"
                )
                return False
            # создаются три потока (thread) для обработки данных
            # в основном потоке разбиваются табличные данные на блоки
            # (self.teams[team]) по идентификаторам (internal_id)
            # во втором потоке из блоков формируются выходные документы (self._collections[document])
            # в третьем потоке документы сохраняются в файлах csv и json
            thread_modules = [self.stage_build_documents, self.stage_print_documents]
            while self.__init_config():
                # перебираем все файлы конфигурации
                # для данного входного файла MS Excel
                # как парвило это один файл, но может быть и несколько
                # для разных листов

                self.num_config = data_reader.set_config(self._page_index)
                self.config_files[self.num_config]["warning"] = []
                is_init = True
                while True:
                    # перебираем все листы исходного Excel файла
                    if not is_init:
                        self.__read_config()
                    is_init = False
                    page = data_reader.get_sheet()
                    if page is None:
                        break
                    self.num_page = page
                    self.__init_data()
                    self.__init_page()
                    self.__set_parameters_page()
                    if not self.__get_header("pattern"):
                        self.colontitul["status"] = 1
                    try:
                        self.ex = Event()
                        threads = [Thread(target=x) for x in thread_modules]
                        for t in threads:
                            t.daemon = True
                            t.start()

                        for self.row, record in enumerate(data_reader):
                            if self.row < 100 and self.row % 10 == 0:
                                print_message(
                                    "         {} {} Обработано: {}                          \r".format(
                                        self.num_page, self.func_inn(), self.row
                                    ),
                                    end="",
                                    flush=True,
                                )
                            record = record[self._col_start :]
                            if self.colontitul["status"] != 2:
                                # Область до или после таблицы
                                if not self.__check_bound_row(self.row):
                                    break
                                self.__check_colontitul(
                                    self.__get_names(record), self.row, record
                                )
                            if self.colontitul["status"] == 2:
                                # Табличная область данных
                                self.__check_record_in_body(record, self.row)

                            if self.row % 100 == 0:
                                print_message(
                                    "         {} {} Обработано: {}                          \r".format(
                                        self.num_page, self.func_inn(), self.row
                                    ),
                                    end="",
                                    flush=True,
                                )
                    finally:
                        self.ex.set()
                        for t in threads:
                            t.join()
        except Exception as ex:
            logger.error(f"{ex}")

        self.__process_finish()

        return True

    def stage_build_documents(self):
        while not self.ex.is_set():
            if len(self._teams) > 50:
                self.__process_record()
        self.__done()

    def stage_print_documents(self):
        while not self.ex.is_set():
            pass
        while len(self._teams) != 0:
            pass
        if self._collections:
            asyncio.run(
                self.write_all_results_async(
                    num_config=self.num_config + 1,
                    num_page=self.num_page + 1,
                    num_file=self.num_file + 1,
                    path_output=self._output,
                    collections=self._collections.copy(),
                    # output_format="json",
                )
            )
        # self._collections.clear()

    def __done(self):
        with ThreadPoolExecutor(max_workers=None) as executor:
            while len(self._teams) != 0:
                executor.submit(self.__process_record())

        # while len(self._teams) != 0:
        #     self.__process_record()

    def __process_record(self) -> None:
        if len(self._teams) == 0:
            return
        try:
            key = next(iter(self._teams))
            team = self._teams[key]
            if self.download_file:
                write_log_time(self.download_file)

            if not self.colontitul["is_parameters"]:
                self.__set_parameters()
            for doc_param in self.__get_config_documents():
                self.__make_collections(doc_param, team)

        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self._teams.popitem(last=False)
            if len(self._teams) % 10 == 0:
                print_message(
                    "         {} {} Осталось обработать: {}                          \r".format(
                        self.num_page, self.func_inn(), len(self._teams)
                    ),
                    end="",
                    flush=True,
                )

    def __make_collections(self, doc_param: dict, team: dict):
        try:
            # для каждого блока (team) определяем свой класс функций
            # для многопотоковой обработки
            _Func = Func(
                self._parameters, self._dictionary, self._column_names, self.is_hash
            )
            doc = self.__set_document(doc_param, team, _Func.func)
            self.__document_split_one_line(doc, doc_param)
        except Exception as ex:
            logger.error(f"{ex}")

    def __process_finish(self) -> None:
        for doc_param in self.__get_config_documents():
            if doc_param.get("func_after"):
                param = {"value": "", "func": doc_param["func_after"]}
                self.func(
                    # fld_param=param, team=man.collections.get(doc_param["name"])
                    fld_param=param,
                    team=self._collections.get(doc_param["name"]),
                )




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
        for key, value in self._column_names.items():
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
    def __append_to_team(self, mapped_record: dict) -> bool:
        team_id = self.__get_team_id(mapped_record)
        if team_id:
            if self._teams.get(team_id):
                self.__update_team(mapped_record, team_id)
            else:
                self._teams[team_id] = mapped_record
        # if team_id:
        #     if self.__check_condition_team(mapped_record):
        #         # Новый идентификатор
        #         self._teams.append(mapped_record)
        #         # self._teams.append(mapped_record)
        #         return True
        #     elif len(self._teams) != 0:
        #         self.__update_team(mapped_record)
        return False

    def __update_team(self, mapped_record: dict, team_id: str = ""):
        if not team_id:
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
        if team_id:
            for key in mapped_record.keys():
                size = self._teams[team_id][key][-1]["row"] + 1
                for mr in mapped_record[key]:
                    self._teams[team_id][key].append(
                        {
                            "row": size,
                            "col": mr["col"],
                            "index": mr["index"],
                            "value": mr["value"],
                            "negative": mr["negative"],
                        }
                    )

    # Проверяем условие завершения группировки записей по текущему идентификатору
    def __check_condition_team(self, mapped_record: dict) -> bool:
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
                            self.is_condition_check = True
                            return True
        return b

    def __get_team_id(self, mapped_record: dict) -> str:
        for p in self.__get_condition_team():
            if mapped_record.get(p["col"]):
                for patt in p["pattern"]:
                    result = self.__get_condition_data(mapped_record[p["col"]], patt)
                    b = False if not result or result.find("error") != -1 else True
                    if b:
                        return result
        return ""

    # Область до или после таблицы
    def __check_bound_row(self, row: int) -> bool:
        if self.__get_row_start() + self.__get_max_rows_heading() < row:
            # Вышли за границу области перед таблицей
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
                self.__add_warning(
                    '\n{}:\nВ загружаемом файле "{}"\nне все колонки найдены \n'.format(
                        self._config._config_name,
                        self._parameters["filename"]["value"][0],
                    )
                )
                if s2:
                    self.__add_warning("\tНайдены колонки:\n{}\n".format(s2.strip()))
                if s1:
                    self.__add_warning("\tНе найдены колонки:\n{}\n".format(s1.strip()))
            else:
                s = "Найдены колонки:"
                for key, value in self._column_names.items():
                    s += f"\n{key} - {value['indexes'][0][POS_INDEX_VALUE]}"
                self.__add_warning(
                    '\n{0}:\nВ загружаемом файле "{1}" \
                \nневерен шаблон нахождения начала области данных(({3})condition_begin_team(\n{2}\n))\n{4}\n'.format(
                        self._config._config_name,
                        self._parameters["filename"]["value"][0],
                        (
                            self.__get_condition_team()[0]["pattern"]
                            if self.__get_condition_team()
                            else ""
                        ),
                        (
                            self.__get_condition_team()[0]["col"]
                            if self.__get_condition_team()
                            else ""
                        ),
                        s,
                    )
                )
            return False
        return True

    def __check_colontitul(self, names: list, row: int, record: list):
        if self.colontitul["status"] == 0:
            if self.__check_headers_status(names):
                if len(self._teams) != 0:
                    self.__done()
                    self.__init_data()
                    self.__set_row_start(row)
        if self.__check_columns(names, row):
            self._row_start = row
        if self.colontitul["status"] == 1:
            if self.__check_stable_columns():
                if (
                    len(self.__get_columns_heading()) <= len(self._column_names)
                ) or self.__check_condition_team(self.__map_record(record)):
                    # переход в табличную область данных
                    self.colontitul["status"] = 2
                    if not self._is_column_service_exist:
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
            else:
                self.__append_to_team(mapped_record)
        if len(self._teams) < 2:
            # добавляем первые записи в таблице в область заголовка
            # (иногда там могут находиться некоторые параметры)
            self.colontitul["head"].append(record)

    # Проверка колонок таблицы на соответствие конфигурации
    def __check_columns(self, names: list, row: int) -> bool:
        is_find = False
        if names:
            last_cols = []
            # список уже добавленных колонок, которые нужно исключить при следующем прохождении
            cols_exclude = list()
            for x in [x["indexes"] for x in self._column_names.values()]:
                cols_exclude.extend([y[POS_INDEX_VALUE] for y in x])
            # сначала проверяем обязательные и приоритетные колонки
            for item_head_column in self.__get_columns_heading():
                if (
                    (not item_head_column["active"] or item_head_column["duplicate"])
                    and item_head_column["pattern"][0]
                    and (
                        not item_head_column["optional"] or item_head_column["priority"]
                    )
                ):
                    if self.__check_column(item_head_column, names, row, cols_exclude):
                        is_find = True
            # потом проверяем остальные колонки
            for item_head_column in self.__get_columns_heading():
                if (
                    (not item_head_column["active"] or item_head_column["duplicate"])
                    and item_head_column["pattern"][0]
                    and item_head_column["optional"]
                    and not item_head_column["priority"]
                ):
                    if item_head_column["after_stable"]:
                        last_cols.append(item_head_column)
                    elif self.__check_column(
                        item_head_column, names, row, cols_exclude
                    ):
                        is_find = True
            # последние колонки (after_stable = True) Прочие услуги
            for item_head_column in last_cols:
                if self.__check_stable_columns() and (
                    row in self.__get_rows_header() or item_head_column["duplicate"]
                ):
                    if self.__check_column(
                        item_head_column, names, row, cols_exclude, True
                    ):
                        is_find = True
        return is_find

    # Проверка колонки таблицы
    def __check_column(
        self,
        item_head_column: dict,
        names: list,
        row: int,
        cols_exclude: list = [],
        is_last: bool = False,
    ) -> dict:
        is_find = False
        patt = ""
        for p in item_head_column["pattern"]:
            patt = patt + ("|" if patt else "") + p
        search_column_names = self.__get_search_names(
            names,
            patt,
            item_head_column,
            cols_exclude if not item_head_column["duplicate"] else [],
        )  # колонки в таблице Excel
        if search_column_names:
            for column_name in search_column_names:
                col_left = self.__get_border(
                    item_head_column, "left", column_name["col"]
                )
                col_right = self.__get_border(
                    item_head_column, "right", column_name["col"]
                )
                if col_left <= column_name["col"] <= col_right:
                    key = item_head_column["name"]
                    if key == "Услуга":
                        # В таблице присутствует колонка в которой указаны названия услуг ЖКУ
                        self._is_column_service_exist = True
                    self._column_names.setdefault(
                        key,
                        {
                            "row": row,
                            "col": item_head_column["col"],
                            "active": True,
                            "indexes": [],
                        },
                    )
                    self._column_names[key]["active"] = True
                    item_head_column["active"] = (
                        True if not item_head_column["after_stable"] else False
                    )
                    if item_head_column["col_data"]:
                        for val in item_head_column["col_data"]:
                            index = get_absolute_index(val, column_name["col"])
                            # добавляем номер колонки из исходной таблицы для суммирования значений
                            # задается параметром "col_data_offset" в настройках
                            if not (
                                (index, val[POS_NUMERIC_IS_NEGATIVE])
                                in self._column_names[key]["indexes"]
                            ):
                                item_head_column["indexes"].append(
                                    (index, val[POS_NUMERIC_IS_NEGATIVE])
                                )
                                self._column_names[key]["indexes"].append(
                                    (index, val[POS_NUMERIC_IS_NEGATIVE])
                                )
                    else:
                        if not (
                            (column_name["col"], False)
                            in self._column_names[key]["indexes"]
                        ):
                            item_head_column["indexes"].append(
                                (column_name["col"], False)
                            )
                            self._column_names[key]["indexes"].append(
                                (column_name["col"], False)
                            )
                            if is_last:
                                self._possible_columns[column_name["col"]] = (
                                    column_name["name"]
                                )
                    item_head_column["row"] = row
                    is_find = True
                    if not is_last:
                        cols_exclude.append(column_name["col"])
                    else:
                        for x in cols_exclude:
                            while (
                                self._column_names[key]["indexes"].count((x, False)) > 0
                            ):
                                self._column_names[key]["indexes"].remove((x, False))
                                item_head_column["indexes"].remove((x, False))
                                self._possible_columns.pop(x)
                    if item_head_column["unique"]:
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
            "%m.%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%y",
            "%d.%m.%y",
            "%d/%m/%y",
            "%B %Y",
            "%m_%Y",
            "%m%Y",
            "%m,%Y",
            "%m,%y",
        ]
        d = None
        for item in self._parameters["period"]["value"]:
            if item:
                for p in patts:
                    try:
                        d = datetime.datetime.strptime(item, p).date()
                        break
                    except:
                        pass
        ls = list()
        if d:
            d = self.__get_period_default(d)
            ls.append(d.replace(day=1).strftime("%d.%m.%Y"))
            ls.append(d.strftime("%d.%m.%Y"))
        else:
            result = regular_calc("19[89][0-9]|20[0-3][0-9]", item)
            if result != None:
                year = result
                month = next(
                    (
                        val
                        for key, val in get_months().items()
                        if regular_calc(key + r"[а-я]{0,5}\s", item)
                    ),
                    None,
                )
                if month:
                    d = datetime.datetime.strptime(
                        f"01.{month}.{year}", "%d.%m.%Y"
                    ).date()
                    d = self.__get_period_default(d)
                    ls.append(d.replace(day=1).strftime("%d.%m.%Y"))
                else:
                    ls.append(self._period.strftime("%d.%m.%Y"))
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
                k = pattern.find("||")
                if k != -1:
                    patt = pattern[:k] if result == "" else pattern
                else:
                    patt = pattern
                value = regular_calc(patt, val["value"])
                if value == None:
                    if result == "":
                        return ""
                else:
                    result += value
        return result

    def __get_data_xls(self):
        ReaderClass = get_file_reader(self._parameters["filename"]["value"][0])
        data_reader = ReaderClass(self._parameters["filename"]["value"][0])
        if not data_reader:
            self.is_file_exists = False
            self.__add_warning(
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
                col = self._column_names[name_field]["indexes"][0][POS_INDEX_VALUE]
            else:
                col = col + 1 if name == "left" else col - 1
        return col

    def __get_rows_header(self) -> set:
        return {x["row"] for x in self._column_names.values()}

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
        data_reader.set_config()
        headers = list()
        try:
            while True:
                page_number = data_reader.get_sheet()
                if page_number is None:
                    break
                sheet_headers = list()
                index = 0
                for record in data_reader:
                    sheet_headers.append(record)
                    index += 1
                    if index > 100:  # self._config._max_rows_heading[0][0]:
                        break
                headers.append(sheet_headers)
        except Exception as ex:
            logger.exception("generate")
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
            self.colontitul["status"] == 0 and len(self._column_names) == 0
        ):
            self.colontitul["head"].append(record)
        elif self.colontitul["status"] == 0 and len(self._column_names) > 0:
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
                if result is not None:
                    b = True
                    if item and item.get("offset") and item["offset"]["pattern"][0]:
                        b = self.__check_column_offset(item, name["col"])
                    if b:
                        results.append(name)
        return results

    def __get_key_from_input_names(self, col: int) -> str:
        for key, value in self._column_names.items():
            if value["col"] == col:
                return key
        return ""

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
        records[-1]["value_rows"] = []
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
            records[-1]["value_rows"] = []
        return records

    def __get_total_value_from_values(
        self, values: list, type_fld: str, pattern: str
    ) -> str:
        value = get_value(type_value=type_fld)
        for val in values:
            if (type_fld == "int" or type_fld == "float") and val[
                POS_NUMERIC_IS_NEGATIVE
            ]:
                value -= get_value(val[POS_VALUE], pattern, type_fld)
            else:
                try:
                    value += get_value(val[POS_VALUE], pattern, type_fld)
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
        value = record["value_o"]
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
        m = set()
        is_main_field = False
        d = next((x for x in self.__get_config_documents() if x["name"] == name), None)
        if d and d["required_fields"]:
            for name_field in d["required_fields"].split(","):
                is_main_field = is_main_field or (name_field.find("(") != -1)
                fld_type = next(
                    (
                        x["type"] + x["offset_type"]
                        for x in d["fields"]
                        if x["name"] == name_field.replace("(", "").replace(")", "")
                    ),
                    "",
                )
                for item in doc[name_field.replace("(", "").replace(")", "")]:
                    val = get_value(str(item["value"]), ".+", fld_type)
                    if (
                        (fld_type == "" or fld_type == "str") and val.strip() != ""
                    ) or ((fld_type == "float" or fld_type == "int") and val != 0):
                        s.add(item["row"])
                        if name_field.find("(") != -1:
                            m.add(item["row"])
        if is_main_field:
            return m & s
        else:
            return s

    def __is_data_depends(
        self, record: dict, doc: dict, doc_param: dict
    ) -> Union[str, bool]:
        if not record["depends"]:
            return True
        fld = record["depends"]
        if doc[fld] and doc[fld][0]["value"]:
            fld_param = self.__get_doc_param_fld(doc_param["name"], fld)
            x = get_value(
                doc[fld][0]["value"], ".+", fld_param["type"] + fld_param["offset_type"]
            )
        else:
            x = ""
        return x


    # если текущая таблица типа словарь (задается в gisconfig_000_00),
    # то формируем глобальный словарь значений
    # для последующих таблиц
    def __build_global_dictionary(self, doc: dict):
        param = {}
        for fld, value in doc.items():
            if fld == "key":
                param = {"value": "key" + doc["key"], "func": "hash"}
                param["key"] = self.func(fld_param=param)
            elif regular_calc("^value", fld):
                param["data"] = value
            else:
                index_key = get_index_key(fld)
                self._dictionary.setdefault(index_key, [])
                if not value in self._dictionary[index_key]:
                    self._dictionary[index_key].append(value)
            if param.get("key") and param.get("data"):
                index_key = get_index_key(param["key"])
                self._dictionary.setdefault(index_key, [])
                if not param["data"] in self._dictionary[index_key]:
                    self._dictionary[index_key].append(param["data"])
        return

    ########################   Изменение конфигурации "на ходу" #################################
    def __dynamic_change_config(self):
        if self.__change_heading():
            self.__change_pp_charges_and_pp_service()

    # Добавляем колонки (услуги), отсутствующие в конфигурации, но имеющиеся в заголовках таблицы
    def __change_heading(self) -> bool:
        bResult = False
        for key, name in self._possible_columns.items():
            b = self.__heading_append(key, name)
            bResult |= b
        return bResult

    # Добавляем услуги, отсутствующие в конфигурации, но имеющиеся в заголовках таблицы
    def __change_pp_charges_and_pp_service(self):
        if len(self._possible_columns) == 0:
            return
        docs = self.__get_list_doc_to_changes()
        for doc in docs:
            flds = self.__get_list_fields_to_update(doc)
            for fld in flds:
                self.__append_to_fld_sub(fld["sub"])
        self._possible_columns = {}

    def __heading_append(self, key: str, name: str) -> bool:
        name = get_ident(name)
        if not self.__is_column_heading_exist(name):
            fld_new = self._config._columns_heading[-1].copy()
            fld_new["name"] = name.replace("*", "_").replace("+", "")
            fld_new["pattern"] = [get_reg(name)]
            fld_new["indexes"] = [(key, False)]
            fld_new["col"] = len(self._config._columns_heading)
            fld_new["after_stable"] = False
            fld_new["duplicate"] = False
            fld_new["activate"] = True
            self._config._columns_heading.append(fld_new)
            self._column_names[fld_new["name"]] = {
                "row": fld_new["row"],
                "col": fld_new["col"],
                "active": True,
                "indexes": fld_new["indexes"],
            }
            return True
        return False

    def __get_list_fields_to_update(self, doc: dict) -> list:
        return [
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

    def __get_list_doc_to_changes(self) -> list:
        return [
            x
            for x in self._config._documents
            if x["name"] in ("pp_charges", "pp_service")
        ]

    def __append_to_fld_sub(self, fld_sub: list) -> None:
        if fld_sub:
            ls = []
            last_rec = fld_sub.pop()
            for name in self._possible_columns.values():
                ls.append(last_rec.copy())
                ls[-1]["func"] = ls[-1]["func"].replace(
                    "Прочие", name.replace(",", " ")
                )
                if len(last_rec["offset_column"]) > 0:
                    l = [
                        x
                        for x in self._config._columns_heading
                        if x["name"] == get_ident(name)
                    ]
                    if l:
                        ls[-1]["offset_column"] = [(l[0]["col"], True, False)]
            last_rec["offset_column"] = [(-1, True, False)]
            fld_sub.clear()
            fld_sub.extend(ls)
            fld_sub.append(last_rec)
            return

    ###############################################################################################################################################
    # --------------------------------------------------- Документы --------------------------------------------------------------------------------
    ################################################################################################################################################
    def __append_to_collection(self, name: str, doc: dict) -> None:
        key = self._page_name if self._page_name else "noname"
        # man.collections.setdefault(name, {key: list()})
        # man.collections[name].setdefault(key, list())
        # man.collections[name][key].append(doc)
        self._collections.setdefault(name, {key: list()})
        self._collections[name].setdefault(key, list())
        self._collections[name][key].append(doc)
        if (
            self.__get_doc_type(name) == "dictionary"
            and doc.get("key")
            and doc.get("value")
        ):
            self.__build_global_dictionary(doc)
        return

    # Формирование документа из части исходной таблицы - team (отдельной области или иерархии)
    # выбранной по идентификатору internal_id
    def __set_document(self, doc_param: dict, team: dict, func) -> dict:
        doc = dict()
        try:
            for fld_item in doc_param["fields"]:  # перебор полей выходной таблицы
                # Формируем данные для записи в выходном файле
                # одно поле (ключ в doc) соответствует одной записи
                doc.setdefault(fld_item["name"], list())
                main_rows_exclude = (
                    dict()
                )  # набор записей для исключение по основному значению
                offset_rows_exclude = set()  # набор записей для исключение по смещению
                for table_row in doc_param["rows_exclude"]:
                    main_rows_exclude[(table_row[0], -1)] = ""
                # собираем все поля (sub): name_attr, name_attr_0, ... , name_attr_N
                fld_records = self.__get_fld_records(fld_item)
                x = 0
                for index, fld_record in enumerate(fld_records):
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
                        main_rows_exclude[(table_row[0], -1)] = ""
                    table_rows = get_value_range(
                        fld_record["row"], len(team[name_field])
                    )
                    for (
                        table_row
                    ) in table_rows:  # обрабатываем все строки области данных
                        if (
                            len(team[name_field]) > table_row[0]
                            and main_rows_exclude.get((table_row[0], -1)) is None
                            and main_rows_exclude.get(
                                (table_row[POS_VALUE], col[POS_VALUE])
                            )
                            is None
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
                                # И получаем из них одно значение (суммирование для чисел, конкатенация для строк)
                                x = self.__get_total_value_from_values(
                                    values=values,
                                    type_fld=fld_record["type"],
                                    pattern=patt,
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
                                                fld_record["offset_column"][0][
                                                    POS_VALUE
                                                ],
                                            )
                                            in offset_rows_exclude
                                        ):
                                            # если есть смещение по таблице относительно текущего значения,
                                            # то берем данные от туда
                                            x_o = self.__get_value_from_offset(
                                                team,
                                                fld_record,
                                                table_row[0],
                                                col[POS_VALUE],
                                            )
                                            if x_o and fld_record["value_o"] != x_o:
                                                fld_record["value_o"] = x_o
                                                if fld_record["func_is_empty"] is False:
                                                    fld_record["value_rows"].append(
                                                        table_row[POS_VALUE]
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
                                    elif (
                                        main_rows_exclude.get(
                                            (table_row[0], col[POS_VALUE])
                                        )
                                        is None
                                    ):
                                        # запоминаем, чтобы не было повтора
                                        main_rows_exclude[
                                            (table_row[0], col[POS_VALUE])
                                        ] = x
                                    break  # пропускаем проверку по остальным шаблонам
                        elif (
                            main_rows_exclude.get(
                                (table_row[POS_VALUE], col[POS_VALUE])
                            )
                            is not None
                            and not fld_record["value"]
                        ):
                            # если значение пустое, берем то что запомнили
                            fld_record["value"] = main_rows_exclude.get(
                                (table_row[POS_VALUE], col[POS_VALUE])
                            )

                    if fld_record["func"]:
                        # если есть, запускаем функцию
                        fld_record["value"] = func(
                            team=team,
                            fld_param=fld_record,
                            row=table_row[0],
                            col=col[0],
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
                    value = (
                        ""
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
                        else str(fld_record["value"]).strip()
                    )
                    # if value:
                    doc[fld_record["name"]].append(
                        {
                            "row": len(doc[fld_record["name"]]),
                            "col": col[0],
                            "value": value,
                        }
                    )
        except Exception as ex:
            logger.error(f"{ex}")
        return doc

    # Разбиваем данные документа по-строчно
    def __document_split_one_line(self, doc: dict, doc_param: dict) -> None:
        try:
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
            elem = dict()
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
                else:
                    pass
        except Exception as ex:
            logger.error(f"{ex}")
        return

    ################################################################################################################################################
    # --------------------------------------------------- Запись в файл ----------------------------------------------------------------------------
    ################################################################################################################################################
    async def write_results_async(
        self,
        num_config: int = 0,
        num_page: int = 0,
        num_file: int = 0,
        path_output: str = "output",
        collections: dict = None,
        output_format: str = None,
    ):
        await self.write_collections_async(
            num_config=num_config,
            num_page=num_page,
            num_file=num_file,
            path_output=path_output,
            collections=collections,
            output_format=output_format,
        )

    async def write_all_results_async(
        self,
        num_config: int = 0,
        num_page: int = 0,
        num_file: int = 0,
        path_output: str = "output",
        collections: dict = None,
        output_format: str = None,
    ):
        await self.write_collections_async(
            num_config=num_config,
            num_page=num_page,
            num_file=num_file,
            path_output=path_output,
            collections=collections,
            output_format=output_format,
        )
        await self.write_logs_async(
            num_config=num_config,
            num_page=num_page,
            num_file=num_file,
            path_output=path_output,
            collections=collections,
        )

    async def write_json_async(self, filename: str, text: str):
        async with aiofiles.open(filename, mode="a+", encoding=ENCONING) as f:
            await f.write(text)

    async def write_csv_async(self, filename: str, records: list):
        names = []
        if not os.path.exists(filename):
            names = [x for x in records[0].keys()]
        async with aiofiles.open(filename, mode="a+", encoding=ENCONING) as f:
            if names:
                writer_head = AsyncDictWriter(
                    f, delimiter=";", lineterminator="\r", fieldnames=names
                )
                await writer_head.writeheader()
            writer_body = AsyncWriter(f)
            for rec in records:
                await writer_body.writerow(rec.values())

    async def write_collections_async(
        self,
        num_config: int = 0,
        num_page: int = 0,
        num_file: int = 0,
        path_output: str = "output",
        collections: dict = None,
        output_format: str = None,
    ) -> None:
        # if not self.__is_init() or len(man.collections) == 0:
        if not self.__is_init() or len(collections) == 0:
            logger.warning(
                'Не удалось прочитать данные из файла "{0} - {1}"\n'.format(
                    self.func_inn(), self._parameters["filename"]["value"][0]
                )
            )
            return

        os.makedirs(pathlib.Path(PATH_OUTPUT, path_output), exist_ok=True)

        id = self.func_id("")
        inn = self.func_inn()
        for name, pages in collections.items():
            for key, records in pages.items():
                file_output = pathlib.Path(
                    PATH_OUTPUT,
                    path_output,
                    f'{inn}{"_"+str(num_file) if num_file != 0 else ""}'
                    + f'{"_"+key.replace(" ","_") if key != "noname" else ""}'
                    + f'{"_"+str(num_page) if num_page!=0 else ""}'
                    + f'{"_"+str(num_config) if num_config!=0 else ""}'
                    + f"{id}_{name}",
                )
                if output_format is None or output_format == "json":
                    jstr = json.dumps(records, indent=4, ensure_ascii=False)
                    await self.write_json_async(f"{file_output}.json", jstr)

                if output_format is None or output_format == "csv":
                    await self.write_csv_async(f"{file_output}.csv", records)

    async def write_logs_async(
        self,
        num_config: int = 0,
        num_page: int = 0,
        num_file: int = 0,
        path_output: str = "output",
        collections: dict = None,
    ) -> None:
        if not self.__is_init() or len(collections) == 0:
            return
        os.makedirs(pathlib.Path(PATH_LOG, path_output), exist_ok=True)
        id = self.func_id("")
        inn = self.func_inn()

        file_output = pathlib.Path(
            PATH_LOG,
            path_output,
            f'{inn}{"_"+str(num_file) if num_file != 0 else ""}'
            + f'{"_"+str(num_page) if num_page!=0 else ""}'
            + f'{"_"+str(num_config) if num_config!=0 else ""}'
            + f"{id}",
        )

        async with aiofiles.open(
            f"{file_output}.log", mode="w", encoding=ENCONING
        ) as file:
            for item in self.config_files:
                await file.write(f"{os.path.basename(str(item['name']))}\n")
            # Параметры
            await file.write(f"{{")
            for key, value in self._parameters.items():
                await file.write(f'\t{key}:"')
                for index in value["value"]:
                    await file.write(f"{index} ")
                await file.write(f'",\n')
            await file.write(f"}},\n")
            # Заголовки таблиц
            await file.write(f"\n{{")
            for item in self._config._columns_heading:
                if item["row"] != -1:
                    await file.write(
                        f"\t({item['col']}){item['name']}:  row={item['row']} col="
                    )
                    for index in item["indexes"]:
                        await file.write(f"{index[POS_INDEX_VALUE]},")
                    await file.write(f'",\n')
            await file.write(f"}},\n\n")
            await file.write("\nself._parameters\n")
            jstr = json.dumps(self._parameters, indent=4, ensure_ascii=False)
            await file.write(jstr)
            await file.write("\nself._config._parameters\n")
            jstr = json.dumps(self._config._parameters, indent=4)
            await file.write(jstr)
            await file.write("\nself._config._columns_heading\n")
            jstr = json.dumps(
                self._config._columns_heading, indent=4, ensure_ascii=False
            )
            await file.write(jstr)

    ################################################################################################################################################
    # ---------------------------------------------- Параметры конфигурации ------------------------------------------------------------------------
    ################################################################################################################################################
    def __set_parameters_page(self):
        self._parameters["number_config"] = {"fixed": False, "value": [self.num_config]}
        self._parameters["number_page"] = {"fixed": False, "value": [self.num_page]}
        self._parameters["number_file"] = {"fixed": False, "value": [self.num_file]}

    def __set_parameters(self) -> None:
        for value in self._parameters.values():
            if not value["fixed"]:
                value["value"] = list()
        for key in self.__get_config_parameters().keys():
            self.__set_parameter(key)

        self._parameters.setdefault("period", {"fixed": False, "value": list()})

        if not self._parameters["period"]["value"]:
            period = self.__get_period_from_file_name()
            self._parameters["period"]["value"].append(period)
        self.__check_period_value()

        self._parameters.setdefault("path", {"fixed": False, "value": list()})
        if not self._parameters["path"]["value"]:
            self._parameters["path"]["value"].append(PATH_OUTPUT)
        self._parameters.setdefault("address", {"fixed": False, "value": list()})
        if not self._parameters["address"]["value"]:
            self._parameters["address"]["value"].append("")
        self.__set_parameters_page()

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
                            if pattern[1:] == name and param.get("value") is not None:
                                self._parameters[name]["value"].append(param["value"])
                            else:
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

    def __get_period_from_file_name(self):
        comp = re.compile(
            "(?:01|02|03|04|05|06|07|08|09|10|11|12)[.,_]?(?:202[0-9]|[2,3][0-9])"
        )
        period = comp.findall(self._parameters["filename"]["value"][0])
        if period:
            return period[0]
        period = datetime.date.today().strftime("%d.%m.%Y")
        return period

    def __get_period_default(self, d: datetime.date):
        if d > self._period and d.replace(
            day=1
        ) == datetime.datetime.today().date().replace(day=1):
            # Меняем, если дата соответствует текущему месяцу
            return self._period
        return d

    def __init_config(self) -> bool:
        if self.index_config < len(self.config_files):
            self._page_index = self.config_files[self.index_config]["sheets"]
            self.index_config += 1
            self.__read_config()
            return True
        else:
            return False

    def __read_config(self) -> None:
        index = self.index_config - 1
        self._config = GisConfig(self.config_files[index]["name"])
        self._page_name = ""
        self._col_start = 0

    def __init_page(self):
        # clear_manager()
        self._is_column_service_exist = (
            False  # Наличие колонки, в которой указаны названия услуг ЖКУ
        )
        self._teams.clear()
        self._collections.clear()  # коллекция выходных документов
        self._possible_columns.clear()
        self._headers.clear()
        self._column_names.clear()

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

    def __is_column_heading_exist(self, name: str) -> bool:
        names = [x for x in self._config._columns_heading if x.get(name) is not None]
        return len(names) != 0

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

    def __get_row_start(self) -> int:
        return (
            get_value_int(self._config._row_start)[0] if self._config._row_start else 0
        )

    def __set_row_start(self, row: int):
        self._config._row_start = [(row, True)]

    def __get_max_rows_heading(self) -> int:
        return get_value_int(self._config._max_rows_heading)[0]

    def __get_header(self, name: str):
        return self._config._header[name]

    @warning_error
    def __get_check(self, name: str):
        return self._config._check[name]

    def __check_controll(self, headers: list, is_warning: bool = False) -> list:
        self.is_check_mode = True
        is_check = False if self._config._check["pattern"][0]["pattern"] else True
        for row in range(self._config._max_rows_heading[0][0]):
            if row < len(headers):
                if not is_check:
                    # Проверка данных перед таблицей
                    for patt in self._config._check["pattern"]:
                        if not patt["is_find"]:
                            patt["is_find"] = any(
                                [regular_calc(patt["pattern"], x) for x in headers[row]]
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
                    self.is_check_mode = False
                    return self.__check_function()
        self.is_check_mode = False
        # Причина, почему не распозданы данные по конфигурации
        if not regular_calc("000_00", self._config._config_name):
            # if not regular_calc("000_00", self._config._config_name):
            mess = f"\n\t{self._config._config_name} :\n"
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
                    "\tНе найдены обязательные колонки согласно шаблонов:\n{0}".format(
                        s
                    )
                )
            if is_check is False:
                x = [
                    x["pattern"]
                    for x in self._config._check["pattern"]
                    if x["is_find"] == False
                ]
                if x:
                    mess += (
                        '\tНе найден текст перед табличными данными:\n\t"{0}"\n'.format(
                            '"\n\t"'.join(x).replace("|", '"\n\t"')
                        )
                    )
            if mess and not mess in self._config._debug:
                # logger.debug("\n" + mess.strip())
                self._config._debug.append(mess)
                if is_warning:
                    self.__add_warning(mess)
        return False

    def __check_incorrect_inn(self) -> bool:
        return (
            self._parameters["inn"]["value"][-1] != "0000000000"
            and self._config._parameters.get("inn")
            and self._config._parameters.get("inn")[0]["pattern"][0] != "@inn"
            and not regular_calc(
                self._parameters["inn"]["value"][-1],
                self._config._parameters.get("inn")[0]["pattern"][0],
            )
        )

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
        self._col_start = 0
        self.colontitul["head"] = list()
        if self.colontitul["foot"]:
            self.colontitul["head"].append(self.colontitul["foot"][-1])
        self.colontitul["foot"] = list()
        for col in self.__get_columns_heading():
            col["active"] = False
        self._column_names = dict()
        self._teams = OrderedDict()
        # self._teams = list()
        self._teams_ref = OrderedDict()

    def __add_warning(self, text: str):
        self.config_files[self.index_config - 1]["warning"].append(text)
