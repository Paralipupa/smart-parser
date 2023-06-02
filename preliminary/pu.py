from utils import get_ident, get_name, get_lines
from settings import *


def pu(lines: list, path: str) -> str:
    names = []
    l : list = get_lines(lines)
    file_name = f'{path}/ini/6_pu.ini'
    with open(file_name, 'w') as file:
        write_section_caption(file,"pu")
        write_section_doc(file, "doc",4,"Приборы учета (ПУ)","pu","internal_id")
        write_section_pu_0(file, lines,"pu",0,"ИНН, ОГРН или OrgID","org_ppa_guid")
        write_section_pu_1(file, lines,"pu",1,"Внутренний идентификатор ПУ","internal_id",names, l)
        write_section_pu_2(file, lines,"pu",2,"Внутренний идентификатор ЛС","account_internal_id")
        write_section(file, lines,"pu",3,"ГИС. Идентификатор ПУ GUID","gis_id")
        write_section(file, lines,"pu",4,"Серийный номер","serial_number")
        write_section(file, lines,"pu",5,"Тип устройства","device_type")
        write_section(file, lines,"pu",6,"Производитель","manufacturer")
        write_section(file, lines,"pu",7,"Модель","model")
        write_section(file, lines,"pu",8,"Показания момент установки. Тариф 1","rr1","_pu")
        write_section(file, lines,"pu",9,"Показания момент установки. Тариф 2","rr2")
        write_section(file, lines,"pu",10,"Показания момент установки. Тариф 3","rr3")
        write_section(file, lines,"pu",11,"Дата установки","installation_date")
        write_section(file, lines,"pu",12,"Дата начала работы","commissioning_date")
        write_section(file, lines,"pu",13,"Дата следующей поверки","next_verification_date")
        write_section(file, lines,"pu",14,"Дата последней поверки","first_verification_date")
        write_section(file, lines,"pu",15,"Дата опломбирования","factory_seal_date")
        write_section(file, lines,"pu",16,"Интервал проверки (кол-во месяцев)","checking_interval")
        write_section_pu_17(file, lines,"pu",17,"Идентификатор услуги","service_internal_id",names, l)
    return file_name

def write_section_caption(file, sec_type: str):
    n = 80
    file.write(";"+''.rjust(n,"#")+"\n")
    file.write(";"+str(f" {sec_type} ".rjust((n-len(sec_type)-2)//2,"-")).ljust(n,"-")+"\n")
    file.write(";"+''.rjust(n,"#")+"\n")
    file.write('\n')
    return

def write_section_doc(file, sec_type: str, sec_number: int, sec_title: str, sec_name: str, required_fields:str=""):
    file.write(f'[{sec_type}_{sec_number}]\n')
    file.write(f'; {sec_title}\n')
    file.write(f'name={sec_name}\n')
    if required_fields:
        file.write(f'required_fields={required_fields}\n')
    file.write('\n')
    return


def write_section_pu_0(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    write_section_head(file,sec_type,sec_number,sec_title,sec_name)
    file.write('pattern=@\n')
    file.write('col_config=0\n')
    file.write('row_data=0\n')
    file.write('func=inn\n')
    file.write('\n')
    return

def write_section_service(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, names:list, l:list, is_ident:bool=True):
    if lines["dic"].get("rr1"):
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        if lines["dic"].get("service"):
            file.write(
                f'offset_col_config={lines["dic"]["service"][0]["col"]}\n')
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'offset_pattern=@{name}\n')
        else:
            file.write('row_data=0\n')
        if lines["dic"].get(f"{sec_name}_{sec_type}"):
            if is_ident:
                file.write(
                    f'func=id+{get_ident(lines["dic"][f"{sec_name}_{sec_type}"][0]["name"])}+ПУ,spacerepl,hash\n')
            else:
                file.write(
                    f'func={get_ident(lines["dic"][f"{sec_name}_{sec_type}"][0]["name"])},spacerepl,hash\n')
        else:
            if is_ident:
                file.write(
                    f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУ,spacerepl,hash\n')
            else:
                file.write(
                    f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")},spacerepl,hash\n')
        if lines["dic"].get(f"{sec_name}_{sec_type}"):
            for i, line in enumerate(lines["dic"][f"{sec_name}_{sec_type}"][1:]):
                file.write(f'[{sec_type}_{sec_number}_{i}]\n')
                file.write(f'; {sec_title}\n')
                if is_ident:
                    file.write(
                        f'func=id+{get_ident(line["name"])}+ПУ,spacerepl,hash\n')
                else:
                    file.write(
                        f'func={get_ident(line["name"])},spacerepl,hash\n')
        else:
            for i, line in enumerate(l[1:]):
                file.write(f'[{sec_type}_{sec_number}_{i}]\n')
                file.write(f'; {sec_title}\n')
                if lines["dic"].get("service"):
                    name = get_name(
                        get_ident(line["name"].split(";")[0]), names)
                    file.write(f'offset_pattern=@{name}\n')
                if is_ident:
                    file.write(
                        f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+ПУ,spacerepl,hash\n')
                else:
                    file.write(
                        f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},spacerepl,hash\n')
    file.write('\n')
    return
    
def write_section_pu_1(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, names:list, l:list):
    write_section_head(file,sec_type,sec_number,sec_title,sec_name)
    write_section_service(file, lines, sec_type, sec_number, sec_title, sec_name, names, l)
    return


def write_section_pu_2(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    write_section_head(file,sec_type,sec_number,sec_title,sec_name)
    file.write("pattern=@0\n")
    file.write("col_config=0\n")
    file.write("row_data=0\n")
    if lines["dic"].get(f"{sec_name}"):
        file.write(
            f'offset_col_config={lines["dic"][f"{sec_name}"][0]["col"]}\n'
        )
        file.write("offset_pattern=.+\n")
    file.write("func=spacerepl,hash\n")
    file.write("\n")
    return

def write_section_pu_17(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, names:list, l:list):
    write_section_head(file,sec_type,sec_number,sec_title,sec_name)
    write_section_service(file, lines, sec_type, sec_number, sec_title, "internal_id", names, l, False)
    return

def write_section(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, sec_prefix:str=""):
    write_section_head(file,sec_type,sec_number,sec_title,sec_name)
    if lines["dic"].get(f"{sec_name}{sec_prefix}"):
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write(
            f'offset_col_config={lines["dic"][f"{sec_name}{sec_prefix}"][0]["col"]}\n'
        )
        file.write("offset_pattern=.+\n")
        if lines["dic"].get(f"{sec_name}{sec_prefix}")[0]['func']:
            file.write(
                f'func={lines["dic"][f"{sec_name}{sec_prefix}"][0]["func"][0]}\n'
            )
        for i, line in enumerate(lines["dic"][f"{sec_name}{sec_prefix}"][1:]):
            file.write(f'[{sec_type}_{sec_number}_{i}]\n')
            file.write(f'; {sec_title}\n')
            if line['func']:
                file.write(
                    f'func={line["func"][0]}\n'
                )
            else:
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
    file.write('\n')

def write_section_head(file, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    file.write(f'[{sec_type}_{sec_number}]\n')
    file.write(f'; {sec_title}\n')
    file.write(f'name={sec_name}\n')
    return

