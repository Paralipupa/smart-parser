import os
import re
import logging
from .excel_base_importer import ExcelBaseImporter
from .helpers import regular_calc, get_config_files, write_list
from .union import UnionData
from .exceptions import InnMismatchException, FatalException, ConfigNotFoundException
# from .search_config_sync import SearchConfig
from .search_config_tasks import SearchConfig
# from .search_config_sync import SearchConfig
from .settings import *

logger = logging.getLogger(__name__)


class Parser:

    def __init__(self,
                 file_name: str = '',
                 inn: str = '',
                 file_config: str = '',
                 union: str = PATH_OUTPUT,
                 path_down: str = PATH_OUTPUT,
                 file_down: str = 'output',
                 hash: str = 'yes'
                 ) -> None:
        self.logs = list()
        self._dictionary = dict()
        self.name = file_name
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download_path = path_down
        self.output_path = re.findall('.+(?=[.])', file_down)[0]
        self.download_file = file_down
        self.is_hash = False if hash == 'no' else True
        self.config_files = get_config_files()


    def start(self) -> list:
        try:
            if not self.name:
                if not self.union:
                    logger.warning(
                        'run with parameters:  [--name|-n]=<file.lst>|<file.xsl>|<file.zip> [[--inn|-i]=<inn>] [[--config|-c]=<config.ini>] [[--union|-u]=<path>')
                else:
                    u = UnionData()
                    return u.start(path_input=os.path.join(PATH_OUTPUT, self.output_path),
                                   path_output=self.download_path,
                                   path_logs=os.path.join(
                        PATH_LOG, self.output_path),
                        file_output=self.download_file)

            else:
                logger.info(f"Архив: {COLOR_CONSOLE['red']}'{os.path.basename(self.name) }'{COLOR_CONSOLE['end']}")
                search_conf = SearchConfig(self.name, self.config_files, self.inn, self.config)
                list_files = search_conf.get_list_files()
                i = 0
                isParser = False
                if list_files:
                    for file_name in list_files:
                        i += 1
                        if file_name['config']:
                            if file_name['config'] != '000':
                                t = regular_calc(
                                    '[0-9]{3}(?=_)', str(file_name['config']))
                                if t != None:
                                    rep: ExcelBaseImporter = ExcelBaseImporter(file_name=file_name['name'],
                                                                            inn=file_name['inn'], config_file=str(file_name['config']))
                                    rep.is_hash = self.is_hash
                                    rep._dictionary = self._dictionary.copy()
                                    logger.info(
                                        f"Начало обработки файла '{os.path.basename(file_name['name'])}'")
                                    if rep.extract():
                                        logger.info(f"Обработка завершена")
                                        isParser = True
                                        self._dictionary = rep._dictionary.copy()
                                        rep.write_collections(num=i, path_output=os.path.join(
                                            PATH_OUTPUT, self.output_path))
                                        rep.write_logs(num=i, path_output=os.path.join(
                                            PATH_LOG, self.output_path))
                                    else:
                                        logger.info(
                                            f"Неудачное завершение обработки")
                                    file_name['warning'] += rep._config._warning
                    file_log = write_list(path_output=os.path.join(
                        PATH_LOG, self.output_path), files=list_files)
                    if self.union:
                        u = UnionData(isParser, file_log)
                        return u.start(path_input=os.path.join(PATH_OUTPUT, self.output_path),
                                       path_output=self.download_path,
                                       path_logs=os.path.join(
                            PATH_LOG, self.output_path),
                            file_output=self.download_file)
                else:
                    logger.info(f"Данные в архиве не распознаны")
        except InnMismatchException as ex:
            return f"{ex}"
        except FatalException as ex:
            return f"{ex._message}"
        except ConfigNotFoundException as ex:
            return f"{ex._message}"
        except Exception as ex:
            logger.exception('Error start')
            return f"{ex}"
        return self.download_path

    @staticmethod
    def get_path(pathname: str) -> str:
        if pathname == 'logs':
            return PATH_LOG
        elif pathname == 'output':
            return PATH_OUTPUT
        elif pathname == 'tmp':
            return PATH_TMP
        else:
            if pathname.find('log') != -1 and os.path.exists(os.path.join(BASE_DIR, pathname)):
                return os.path.join(BASE_DIR, pathname)
        return ''
