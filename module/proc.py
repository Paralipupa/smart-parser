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

logger = logging.getLogger(name)
manager = Manager()
man_list = manager.list()
COUNTER = Value("i", 0)
FLAG = Value("b", True)
DOWNLOAD_FILE = manager.dict()
DOWNLOAD_FILE["name"] = ""
lock = Lock()

class Parser:
    def init(self, file_name: str = "", inn: str = "", file_config: str = "", union: str = PATH_OUTPUT, path_down: str = PATH_DOWNLOAD, file_down: str = "output", hash: str = "yes", is_daemon: bool = False) -> None:
        self.logs = list()
        self.name = file_name
        self._period = datetime.date.today().replace(day=1)
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download_path = path_down
        self.output_path = os.path.basename(re.findall(".+(?=[.])", file_down)[0] if re.findall(".+(?=[.])", file_down) else "")
        self.output_path = self.output_path if self.output_path else (inn if inn else "output")
        self.is_hash = False if hash == "no" else True
        self.check_tarif = False
        self.is_daemon = is_daemon
        self.config_files = get_config_files()
        self.mem = round(psutil.virtual_memory().available / 1024**3, 2)
        self.list_files = None

    def run(self):
        print(f"Processing file {self.file_name}")
        # Тело метода run (необходимо добавить реальную логику обработки)

def stage_finish():
    print("All tasks are completed. Performing final stage...")

def manage_tasks():
    file_names = ["file1.xlsx", "file2.xlsx", "file3.xlsx"]
    parsers = [Parser(file_name=name) for name in file_names]

    with Pool(processes=3) as pool:
        pool.map(lambda parser: parser.run(), parsers)

    stage_finish()

def run_in_background():
    main_process = Process(target=manage_tasks)
    main_process.start()
    return main_process

if name == "main":
    run_in_background()
    print("Main module is running in the background...")