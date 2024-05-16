import os
import re
import logging
import shutil
import datetime
import psutil
from functools import partial
from time import time, gmtime, strftime, sleep
from pathlib import Path
from module.excel_base_importer import ExcelBaseImporter
from module.helpers import get_config_files, write_list, check_tarif, write_log_time
from module.union import UnionData
from module.exceptions import (
    InnMismatchException,
    FatalException,
    ConfigNotFoundException,
    CheckTarifException,
)
from module.search_config_tasks import SearchConfig
from module.settings import *

from multiprocessing import Process, Pool, Manager, Lock, Value, Queue, Semaphore
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


logger = logging.getLogger(__name__)
manager = Manager()
man_list = manager.list()
man_queue = manager.Queue()
DOWNLOAD_FILE = manager.dict()
DOWNLOAD_FILE["name"] = ""
DOWNLOAD_FILE["period"] = ""
lock = Lock()


class Parser:
    def __init__(
        self,
        file_name: str = "",
        inn: str = "",
        file_config: str = "",
        union: str = PATH_OUTPUT,
        path_down: str = PATH_DOWNLOAD,
        file_down: str = "output",
        hash: str = "yes",
        is_daemon: bool = False,
    ) -> None:
        self.logs = list()
        self.name = file_name
        self._period = datetime.date.today().replace(day=1)
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download_path = path_down
        self.output_path = os.path.basename(
            re.findall(".+(?=[.])", file_down)[0]
            if re.findall(".+(?=[.])", file_down)
            else ""
        )
        if not self.output_path:
            self.output_path = inn if inn else "output"
        self.is_hash = False if hash == "no" else True
        self.check_tarif = False
        self.is_daemon = is_daemon
        self.config_files = get_config_files()
        self.mem = round(psutil.virtual_memory().available / 1024**3, 2)
        self.list_files = None
        self.isParser = False
        self.file_log = ""
        self.count = 0
        self.download_file = self.get_file_output(file_down)
        clear_manager()

    def start(self) -> list:
        try:
            DOWNLOAD_FILE["name"] = self.download_file
            DOWNLOAD_FILE["period"] = self._period
            put_queue(DOWNLOAD_FILE["name"])
            nstart = time()
            if not self.name:
                self.final_union(nstart)
            else:
                logger.info(
                    f"Архив: {COLOR_CONSOLE['red']}'{os.path.basename(self.name) }'{COLOR_CONSOLE['end']}"
                )
                self.run_background(nstart)
        except (FatalException, ConfigNotFoundException, CheckTarifException) as ex:
            logger.error(f"{ex}")
            put_queue(f"{ex._message}")
        except (InnMismatchException, Exception) as ex:
            logger.error(f"{ex}")
            put_queue(f"{ex}")
        return get_queue()


    def run_background(self, nstart):
        main_process = Process(target=self.manage_tasks, args=(nstart,))
        main_process.start()
        if self.is_daemon:
            main_process.join(0)
        else:
            main_process.join()
        return

    def process_run(self, data):
        self.stage_extract(data[0], data[1])

    def manage_tasks(self, nstart):
        self.list_files = self.get_config()
        if self.list_files:
            self.count = len(self.list_files)
            parsers_0 = [
                (name, index)
                for index, name in enumerate(self.list_files, 1)
                if "_000_" in str(name["config"][0]["name"])
            ]
            parsers_1 = [
                (name, index)
                for index, name in enumerate(self.list_files, len(parsers_0) + 1)
                if not "_000_" in str(name["config"][0]["name"])
            ]
            with ProcessPoolExecutor(max_workers=4) as executor:
                executor.map(self.process_run, parsers_0)
            with ProcessPoolExecutor(max_workers=8) as executor:
                executor.map(self.process_run, parsers_1)
            self.stage_finish(nstart)
        else:
            logger.info(
                f"Данные в архиве не распознаны {strftime('%H:%M:%S', gmtime(time()-nstart))}"
            )
            if self.is_daemon:
                file_name = os.path.join(self.download_path, DOWNLOAD_FILE["name"])
                write_log_time(file_name, True)
            shutil.copy(
                os.path.join(BASE_DIR, "doc", "error.txt"),
                os.path.join(self.download_path, "error.txt"),
            )
            if not self.is_daemon:
                put_queue("error.txt")
            else:
                file_name = os.path.join(self.download_path, DOWNLOAD_FILE["name"])
                write_log_time(file_name, True)
                put_queue("error.txt")
        return

    def stage_finish(self, nstart):
        self.file_log = write_list(
            path_output=os.path.join(PATH_LOG, self.output_path),
            files=self.list_files,
        )
        self.final_union(nstart)
        return

    def stage_extract(self, file_name: dict, counter: int):
        if file_name["config"] and file_name["config"][0]["sheets"]:
            dictionary = get_dictionary_manager()
            rep: ExcelBaseImporter = ExcelBaseImporter(
                file_name=file_name["name"],
                inn=file_name["inn"],
                config_files=file_name["config"],
                index=counter,
                output=self.output_path,
                period=self._period,
                is_hash=self.is_hash,
                dictionary=dictionary,
                download_file=(
                    os.path.join(self.download_path, DOWNLOAD_FILE["name"])
                    if self.is_daemon
                    else ""
                ),
                progress=round(((counter - 1) / self.count) * 100, 2),
            )
            if self.check_tarif is False and not rep._dictionary.get("tarif") is None:
                self.check_tarif = True
                mess = check_tarif(rep._dictionary.get("tarif"))
                if mess:
                    raise CheckTarifException(mess)
            free_mem = round(psutil.virtual_memory().available / 1024**3, 2)
            logger.info(
                f"({counter}/{self.count}) (dict={len(dictionary)}) {free_mem}/{self.mem}({round(100*free_mem/self.mem,2)}%) "
                + f"Начало обработки файла '{os.path.basename(file_name['name'])}'({Path(file_name['config'][0]['name']).stem})"
            )
            self.inn = rep.extract()
            if self.inn:
                if not self.is_daemon:
                    DOWNLOAD_FILE["name"] = self.get_file_output(DOWNLOAD_FILE["name"])
                    put_queue(DOWNLOAD_FILE["name"])
                logger.info(f"Обработка завершена      ")
                set_dictionary_manager(rep._dictionary)
                self.isParser = True
                if rep._parameters.get("period"):
                    if (
                        DOWNLOAD_FILE["period"]
                        > datetime.datetime.strptime(
                            rep._parameters["period"]["value"][0],
                            "%d.%m.%Y",
                        ).date()
                    ):
                        DOWNLOAD_FILE["period"] > datetime.datetime.strptime(
                            rep._parameters["period"]["value"][0],
                            "%d.%m.%Y",
                        ).date()

            else:
                logger.info(f"Неудачное завершение обработки")

    def get_config(self):
        search_conf = SearchConfig(
            file_name=self.name,
            config_files=self.config_files,
            inn=self.inn,
            file_conf=self.config,
            is_daemon=self.is_daemon,
        )
        list_files = search_conf.get_list_files()
        return list_files

    def final_union(self, nstart):
        result = ""
        if self.union:
            logger.info(f"Сборка документов")
            u = UnionData(
                isParser=self.isParser,
                file_log=self.file_log,
                path_input=os.path.join(PATH_OUTPUT, self.output_path),
                path_output=self.download_path,
                file_output=DOWNLOAD_FILE["name"],
                is_daemon=self.is_daemon,
                inn=self.inn,
            )
            result = u.start()
            logger.info(
                f"Окончание сборки {strftime('%H:%M:%S', gmtime(time()-nstart))} {'. Архив не сформирован' if bool(result) is False else ''}"
            )
        return result

    def download(self):
        if not self.union:
            logger.warning(
                "run with parameters:  [--name|-n]=<file.lst>|<file.xsl>|<file.zip> [[--inn|-i]=<inn>] [[--config|-c]=<config.ini>] [[--union|-u]=<path>"
            )
        else:
            u = UnionData(
                path_input=os.path.join(PATH_OUTPUT, self.output_path),
                path_output=self.download_path,
                file_output=DOWNLOAD_FILE["name"],
                inn=self.inn,
            )
            return u.start()

    def get_file_output(self, file_name) -> str:
        return (
            file_name
            if file_name
            and (
                not file_name.startswith("output")
                or (self.inn and self.inn.startswith("0000"))
            )
            else (
                (
                    f'{self.inn if self.inn else "output"}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip'
                )
            )
        )

def get_path(pathname: str) -> str:
    if pathname == "logs":
        return PATH_LOG
    elif pathname == "output":
        return PATH_OUTPUT
    elif pathname == "tmp":
        return PATH_TMP
    else:
        if pathname.find("log") != -1 and os.path.exists(
            os.path.join(BASE_DIR, pathname)
        ):
            return os.path.join(BASE_DIR, pathname)
    return ""

def clear_manager():
    del man_list[:]


def put_queue(val):
    try:
        while True:
            man_queue.get_nowait()
    except:
        pass
    finally:
        man_queue.put(val)


def get_queue():
    return man_queue.get()


def set_dictionary_manager(l: list):
    with lock:
        if l:
            for key, value in l.items():
                man_list.append((key, value))


def get_dictionary_manager() -> list:
    d: dict = dict()
    with lock:
        for i in range(len(man_list)):
            x = man_list[i]
            d[x[0]] = x[1]
    return d
