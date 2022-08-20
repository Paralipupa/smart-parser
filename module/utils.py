import zipfile
import os
import re
import argparse
from datetime import datetime
from report.report_001_00 import Report_001_00
from .gisconfig import PATH_OUTPUT, PATH_LOG, PATH_TMP, PATH_CONFIG
import pathlib
import logging

db_logger = logging.getLogger('parser')
config_files = []


def createParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', nargs='?')
    parser.add_argument('-i', '--inn', nargs='?')
    parser.add_argument('-c', '--config', nargs='?')
    parser.add_argument('-u', '--union', nargs='?')
    return parser

def remove_files(path: str):
    os.remove(path=path)


def get_config_files():
    files = [x for x in os.listdir(PATH_CONFIG) if re.search(
        'gisconfig_[0-9]{3}_[0-9]{2}[0-9a-z_\-,()]*\.ini', x, re.IGNORECASE)]
    # сортировка: 002_05a.ini раньше чем 002_05.ini
    files = sorted(files, key=lambda x: (
        x[10:13], x[14:17] if x[16:17] != '.' else x[14:16]+'я'))
    return files


def get_files(namespace : argparse.Namespace) -> list:
    inn = namespace.inn
    file_conf = namespace.config
    file_name = namespace.name
    global config_files
    config_files = get_config_files()
    list_files = list()
    zip_files = list()

    if file_name.find('.lst') != -1:
        zip_files = get_list_files(file_name)
    elif file_name.lower().find('.zip') != -1:
        zip_files.append({'file': file_name, 'inn': inn, 'config': ''})

    if zip_files:
        for file_name in zip_files:
            inn = get_inn(filename=file_name['file'])
            file_name['inn'] = inn if inn else file_name['inn']
            file_name['config'] = [
                file_conf] if file_conf else file_name['config']
            list_files += get_extract_files(archive_file=file_name)
        list_files = get_file_config(list_files)
    else:
        list_files.append(
            {'name': file_name, 'config': file_conf, 'inn': inn, 'warning': list(), 'zip': ''})

    return list_files


def get_list_files(name: str) -> list:
    l = list()
    with open(name, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() and line.strip()[0] != ';':
                index = line.find('|')
                if index != -1:
                    line = line[:index]
                index = line.find(';')
                result = []
                if index != -1:
                    result = re.findall(
                        """(?<=;)(?:(?:\s*[0-9]{3}(?:(?:_[0-9]{2}[a-z0-9_]*)|\s*)))?""", line)
                    line = line[:index]
                if line.strip():
                    l.append({'file': line.strip(), 'inn': '', 'config': []})
                    for item in result:
                        if item.strip() == '000':
                            l[-1]['config'].append(item.strip())
                        else:
                            l[-1]['config'].append(
                                f'{PATH_CONFIG}/gisconfig_{item.strip()}.ini' if item.strip() else '')
    return l


def get_file_config(list_files: list) -> str:
    ls_new = list()
    i = 0
    for item in list_files:
        data_file = {'name': item['name'], 'config': item['config'],
                     'inn': item['inn'], 'warning': list(), 'records': None, 'zip': item['zip']}
        if item['config']:
            ls_new.append(data_file)
        else:
            ls_new.append(get_data_file(
                data_file, config_files, i, len(list_files)))
        i += 1
    return ls_new


def get_data_file(data_file: dict, config_files: list, j: int, m: int) -> dict:
    ls = list()
    i = 0
    for conf_file in config_files:
        data_file = __check_config(data_file, conf_file)
        print('Поиск конфигураций: {}%   \r'.format(
            round((j*len(config_files)+i)/(m*len(config_files))*100, 0)), end='', flush=True)
        i += 1
        if data_file['config']:
            break
    return data_file


def __check_config(data_file, conf_file):
    if conf_file.find('.ini') != -1:
        file_config = pathlib.Path(PATH_CONFIG, f'{conf_file}')
        rep = Report_001_00(file_name=data_file['name'],
                            config_file=str(file_config), inn=data_file['inn'], data=data_file['records'])
        if rep.is_file_exists:
            if not rep._config._is_unique:
                if rep.check():
                    data_file['config'] = file_config
                    return data_file
                elif rep._config._warning:
                    for w in rep._config._warning:
                        data_file['warning'].append(w)
                data_file['records'] = rep._headers
        if not rep.is_file_exists:
            data_file['warning'].append(
                'ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(data_file['name']))
            return data_file
    return data_file


def get_extract_files(archive_file: str, extract_dir: str = 'tmp') -> list:
    if not os.path.exists(archive_file['file']):
        return []
    z = zipfile.ZipFile(archive_file['file'], 'r')
    z.extractall(extract_dir)
    list_files = list()
    i = 0
    for name in z.namelist():
        try:
            old_name = pathlib.Path(extract_dir, name)
            new_name = get_name_decoder(str(old_name))
            s = get_path_decoder(old_name)
            os.rename(s, new_name)
        except Exception as ex:
            pass
        if re.search('\.xls', new_name):
            conf = archive_file['config'][i] if archive_file['config'] else ''
            list_files.append({'name': new_name,
                              'inn': archive_file['inn'],
                               'config': conf,
                               'warning': list(),
                               'zip': archive_file['file']})
            if i < len(archive_file['config'])-1:
                i += 1

    return list_files


def get_path_decoder(path: pathlib.PosixPath) -> str:
    s = [get_name_decoder(x) for x in path.parts[:-1]]
    s += [path.parts[-1]]
    return str(pathlib.Path(*s))


def get_name_decoder(name: str) -> str:
    try:
        return name.encode('cp437').decode('cp866')
    except Exception as ex:
        return name


def get_inn(filename: str) -> str:
    pattern = '[0-9]{10,12}'
    match = re.search(pattern, filename)
    if match:
        return match.group(0)
    return ''


def write_list(files):

    os.makedirs(PATH_LOG, exist_ok=True)

    file_output = pathlib.Path(
        PATH_LOG, f'session{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
    with open(file_output, 'w') as file:
        for item in files:
            if item['config']:
                file.write(
                    f"{item['inn']} \t {item['name']} \t {item['config']}\n")
        file.write('\n\n')
        for item in files:
            if item['warning']:
                s = ' '.join([x for x in item['warning']]).strip()
                file.write(f"{item['inn']} \t {item['name']} \t {s}\n")
                file.write('\n')
