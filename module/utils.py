import zipfile
import os
import re
import argparse
import pathlib
import hashlib
from datetime import datetime
from report.report_001_00 import Report_001_00
from .gisconfig import print_message, PATH_OUTPUT, PATH_LOG, PATH_TMP, PATH_CONFIG
from .settings import *

config_files = []


def getArgs() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', nargs='?')
    parser.add_argument('-i', '--inn', nargs='?')
    parser.add_argument('-c', '--config', nargs='?')
    parser.add_argument('-u', '--union', nargs='?')
    parser.add_argument('-x', '--hash', nargs='?')
    return parser


def remove_files(path: str):
    os.remove(path=path)


def get_config_files():
    try:
        files = [x for x in os.listdir(PATH_CONFIG) if re.search(
            'gisconfig_[0-9]{3}_[0-9]{2}[0-9a-z_\-,()]*\.ini', x, re.IGNORECASE)]
        # сортировка: 002_05a.ini раньше чем 002_05.ini
        files = sorted(files, key=lambda x: (
            x[10:13], x[14:17] if x[16:17] != '.' else x[14:16]+'я'))
    except Exception as ex:
        files = []
    return files


def get_files(file_name: str, inn: str, file_conf: str) -> list:
    global config_files
    config_files = get_config_files()
    list_files = list()
    zip_files = list()
    print_message('', flush=True)

    if file_name.find('.lst') != -1:
        zip_files = get_list_files(file_name)
    elif file_name.lower().find('.zip') != -1:
        zip_files.append({'file': file_name, 'inn': inn, 'config': ''})

    if zip_files:
        for file_name in zip_files:
            file_name['inn'] = inn if inn else get_inn(
                filename=file_name['file'])
            file_name['config'] = [
                file_conf] if file_conf else file_name['config']
            list_files += get_extract_files(archive_file=file_name)
    else:
        list_files.append(
            {'name': file_name, 'config': file_conf, 'inn': inn, 'warning': list(), 'zip': ''})
    list_files = get_file_config(list_files)
    list_files = sorted(list_files, key=lambda x: (
        str(x['config']), str(x['name'])))

    return list_files


def get_list_files(name: str) -> list:
    l = list()
    with open(name, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() and line.strip()[0] != ';':
                index = line.find('|')
                if index != -1:
                    line = line[:index]
                index = line.find(';')
                result = []
                if index != -1:
                    try:
                        patt = r"(?<=;)(?:(?:\s*[0-9]{3}(?:(?:_[0-9]{2}[a-z0-9_]*)|\s*)))?"
                        result = re.findall(
                            patt, line)
                    except Exception as ex:
                        pass

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
            ls_new.append(__config_process(data_file, item['config']))
        else:
            ls_new.append(__config_find(
                data_file, config_files, i, len(list_files)))
        i += 1
    return ls_new


def __config_find(data_file: dict, config_files: list, j: int, m: int) -> dict:
    ls = list()
    i = 0
    for conf_file in config_files:
        print_message('          Поиск конфигураций: {}%   \r'.format(
            round((j*len(config_files)+i)/(m*len(config_files))*100, 0)), end='', flush=True)
        data_file = __config_process(
            data_file, pathlib.Path(PATH_CONFIG, f'{conf_file}'))
        if data_file['config']:
            break
        i += 1
    return data_file


def __config_process(data_file: dict, file_config):
    rep = Report_001_00(file_name=data_file['name'],
                        config_file=str(file_config), inn=data_file['inn'])
    if rep.is_file_exists:
        if not rep._config._is_unique:
            if rep.check():
                data_file['config'] = file_config
                return data_file
            elif rep._config._warning:
                for w in rep._config._warning:
                    data_file['warning'].append(w)
            data_file['config'] = ''
    if not rep.is_file_exists:
        data_file['warning'].append(
            'ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(data_file['name']))
    return data_file


def get_extract_files(archive_file: str, extract_dir: str = PATH_TMP, ext: str = r'.xls') -> list:
    if not os.path.exists(archive_file['file']):
        return []
    list_files = []
    names = []
    with zipfile.ZipFile(archive_file['file'], 'r') as zip_file:
        names = [text_file.filename for text_file in zip_file.infolist()]
        for z in names:
            zip_file.extract(z, extract_dir)
    i = 0
    for name in names:
        try:
            old_name = pathlib.Path(extract_dir, name)
            new_name = get_name_decoder(str(old_name))
            s = get_path_decoder(old_name)
            os.rename(s, new_name)
        except Exception as ex:
            pass
        if re.search(ext, new_name):
            conf = archive_file['config'][i] if archive_file.get(
                'config') else ''
            list_files.append({'name': new_name,
                              'inn': archive_file.get('inn', ''),
                               'config': conf,
                               'warning': list(),
                               'zip': archive_file.get('file', '')})
            if i < len(archive_file.get('config', ''))-1:
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


def write_list(path_output: str, files: list):
    os.makedirs(path_output, exist_ok=True)
    is_warning = False
    mess = ''
    mess_conf = ''
    file_output = pathlib.Path(
        path_output, f'session{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
    with open(file_output, 'w', encoding=ENCONING) as file:
        for item in files:
            if item['warning']:
                s = ' '.join([f'{x}' for x in item['warning']]).strip()
                mess += "{0}{1}\t{2}: \n{3}".format(
                    '\n\n' if mess != '' else '', item['inn'], os.path.basename(item['name']), s)
                is_warning = True
        for item in files:
            if item['config']:
                mess_conf += f"{item['inn']} \t {os.path.basename(item['name'])} \t ({os.path.basename(item['config'])})\n"
            else:
                file.write(
                    f"{item['inn']} \t {os.path.basename(item['name'])} \t - файл не распознан\n")
                is_warning = True
        if is_warning:
            file.write('\n')
            file.write(mess)
        else:
            file.write(mess_conf)
    return file_output if is_warning else ''


def get_hash_file(file_name: str):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    md5 = hashlib.md5()

    with open(file_name, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()
