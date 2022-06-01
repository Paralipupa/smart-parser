import zipfile
import os
import re
import sys
from datetime import datetime
from report.report_001_00 import Report_001_00
from .gisconfig import PATH_OUTPUT, PATH_LOG, PATH_TMP, PATH_CONFIG
import pathlib
import logging

db_logger = logging.getLogger('parser')

def remove_files(path: str):
    os.remove(path=path)

def get_files():
    if len(sys.argv)<=1: 
            logging.warning('run with parameters:  <file.lst>|<file.xsl>|<file.zip> [<inn>] [<config.ini>]')
            exit()
    inn = ''
    file_conf = ''
    if len(sys.argv)>2: inn = sys.argv[2]
    if len(sys.argv)>3: file_conf = sys.argv[3]

    file_name = sys.argv[1]
    list_files = list()
    zip_files = list()

    if file_name.find('.lst') != -1:
        zip_files = get_list_files(sys.argv[1])
    elif file_name.lower().find('.zip') != -1:
        zip_files.append({'file': file_name, 'inn':inn})
    
    if zip_files:
        for file_name in zip_files:
            inn = get_inn(filename=file_name['file'])
            file_name['inn'] = inn if inn else file_name['inn']
            list_files += get_extract_files(archive_file=file_name)

        list_files = get_file_config(list_files)
    else:
        list_files.append({'name': file_name, 'config': file_conf, 'inn': inn, 'warning':list()})

    return list_files

def get_list_files(name: str) ->list:
    l = list()
    with open(name, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() and line.strip()[0] != ';':
                l.append({'file':line.strip(),'inn':''})
    return l

def get_file_config(list_files: list) -> str:
    ls_new = list()
    config_files = [x for x in os.listdir(PATH_CONFIG)]
    config_files.sort(reverse=True)
    i=0
    for item in list_files:
        ls_new.append({'name': item['name'], 'config': '', 'inn': item['inn'], 'warning':list()})
        for conf_file in config_files:
            if conf_file.find('.ini') != -1:
                file_config = pathlib.Path(PATH_CONFIG, f'{conf_file}') 
                rep = Report_001_00(file_name=item['name'],
                                    config_file=str(file_config))
                if  rep.is_file_exists:
                    if rep.check(is_warning=False):
                        ls_new[-1]['config'] = file_config
                        break
                    elif rep._config._warning:
                        for w in rep._config._warning:
                            ls_new[-1]['warning'].append(w)
                if not rep.is_file_exists: 
                    ls_new[-1]['warning'].append('ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(item['name']))
                    break
        i+=1
        print('Поиск конфигураций: {}%   \r'.format(round(i/len(list_files)*100,0)), end='', flush=True)

    return ls_new

def get_extract_files(archive_file: str, extract_dir: str = 'tmp') -> list:
    if not os.path.exists(archive_file['file']):
        return []
    z = zipfile.ZipFile(archive_file['file'], 'r')
    z.extractall(extract_dir)
    list_files = list()
    for name in z.namelist():
        try:
            new_name = str(pathlib.Path(extract_dir, name) )
            new_name = new_name.encode('cp437').decode('cp866')
            os.rename(pathlib.Path(extract_dir, name), new_name)
            # os.rename(f'{extract_dir}/{name}', new_name)
        except Exception as ex:
            pass
        list_files.append({'name': new_name, 'config': '', 'inn': archive_file['inn'], 'warning':list()})
        
    return list_files


def get_inn(filename: str) -> str:
    pattern = '[0-9]{10,12}'
    match = re.search(pattern, filename)
    if match:
        return match.group(0)
    return ''

def write_list(files):

    os.makedirs(PATH_LOG, exist_ok=True)

    file_output = pathlib.Path(PATH_LOG, f'session{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
    with open(file_output, 'w') as file:
        for item in files:
            if item['config']:
                file.write(f"{item['inn']} \t {item['name']} \t {item['config']}\n")
        file.write('\n\n')
        for item in files:
            if item['warning']:
                s = ' '.join([x for x in item['warning']]).strip()
                file.write(f"{item['inn']} \t {item['name']} \t {s}\n")
                file.write('\n')
