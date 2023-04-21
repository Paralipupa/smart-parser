from utils import get_lines
from settings import *

def pp_service(lines:list, path: str):
    l = get_lines(lines)
    file_name = f'{path}/ini/5_pp_service.ini'
    with open(file_name, 'w') as file:
        file.write(';########################################################################################################################\n')
        file.write(';----------------------------------------------------------- pp_service -------------------------------------------------\n')
        file.write(';########################################################################################################################\n')
        file.write('[doc_3]\n')
        file.write(';Документ. Услуги (pp_service.csv)\n')
        file.write('name=pp_service\n\n')
        file.write('required_fields=name\n\n')

        file.write('[pp_service_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[pp_service_1]\n')
        file.write('; Внутренний идентификатор услуги \n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=internal_id\n')
        file.write('pattern=.+\n')        
        file.write('row_data=0\n')

        if lines["dic"].get("service"):
            file.write(
                f'col_config={lines["dic"].get("service", {"col":20})["col"]}\n')
            file.write(f"func=hash\n")
        else:
            file.write('col_config=0\n')
            file.write(
                f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash\n\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[pp_service_1_{i}]\n')
                file.write('; Внутренний идентификатор услуги\n')
                file.write(f'; {line["name"].rstrip()}\n')
                file.write(f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash\n')
        file.write('\n')

        for k in [2,3]:
            file.write(f'[pp_service_{k}]\n')
            if k == 2:
                file.write('; наименование в 1с\n')
                file.write('; Строка 200\n')
                file.write('name=name\n')
            else:
                file.write('; вид в 1с (полное наименование)\n')
                file.write('; Строка 200\n')
                file.write('name=kind\n')
            file.write('pattern=.+\n')
            file.write('row_data=0\n')
            if lines["dic"].get("service"):
                file.write(
                    f'col_config={lines["dic"].get("service", {"col":20})["col"]}\n')
            else:
                file.write('col_config=0\n')
                file.write(f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")}\n\n')
                for i, line in enumerate(l[1:]):
                    file.write(f'[pp_service_{k}_{i}]\n')
                    file.write(f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}\n')
            file.write('\n')

        file.write('[pp_service_4]\n')
        file.write('; код услуги в ГИС\n')	
        file.write('name=gis_code\n\n')
    return file_name