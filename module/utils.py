import zipfile
import os
import re
import sys
from report.report_001_00 import Report_001_00
from .gisconfig import GisConfig

import logging
import traceback

db_logger = logging.getLogger('parser')

path_config = 'config'
path_tmp = 'config'


def remove_files(path: str):
    os.remove(path=path)


def get_extract_files(archive_file: str, extract_dir: str = 'tmp') -> list:
    if not os.path.exists(archive_file):
        return []
    z = zipfile.ZipFile(archive_file, 'r')
    z.extractall(extract_dir)
    list_files = list()
    for name in z.namelist():
        new_name = '{}/{}'.format(extract_dir,
                                  name.encode('cp437').decode('cp866'))
        os.rename(f'{extract_dir}/{name}', new_name)
        list_files.append(new_name)
    return list_files


def get_inn(filename: str) -> str:
    pattern = '[0-9]{10,12}'
    match = re.search(pattern, filename)
    if match:
        return match.group(0)
    return ''


def get_files():
    list_files = list()
    inn = ''
    if len(sys.argv) in (2,3):
        file_name = sys.argv[1]
        inn = get_inn(filename=file_name)
        if file_name.lower().find('.zip') != -1:
            list_files = get_extract_files(archive_file=file_name)
        else:
            list_files.append(file_name)
        list_files = get_file_config(list_files)
    else:
        if len(sys.argv) < 3:
            print('run with parameters:  <file.xsl>|<file.zip> [<inn>] [<config.ini>]')
            exit()
        inn = sys.argv[2]
        list_files.append({'name': sys.argv[1], 'config': ''})
        if len(sys.argv) >= 4:
            list_files[-1]['config'] = sys.argv[3]
    return list_files, inn


def get_file_config(list_files: list) -> str:
    ls_new = list()
    config_files = [[x, False] for x in os.listdir(path_config)]
    for file_name in list_files:
        ls_new.append({'name': file_name, 'config': ''})
        for file in config_files:
            if not file[1] and file[0].find('.ini') != -1:
                file_config = f'{path_config}/{file[0]}'
                rep = Report_001_00(file_name=file_name,
                                    config_file=file_config)
                if not rep.is_file_exists:
                    exit()
                else:
                    if rep.check(is_warning=False):
                        ls_new[-1]['config'] = file_config
                        file[1] = True
                        break
    return ls_new
