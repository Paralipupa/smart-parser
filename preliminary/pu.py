from utils import get_ident, get_name,get_lines
from settings import *

def pu(lines:list, path: str)->str:
    names = []
    l = get_lines(lines)
    file_name = f'{path}/ini/6_pu.ini'
    with open(file_name, 'w') as file:
        file.write(';########################################################################################################################\n')
        file.write(';---------------------------------------------------------------- pu ----------------------------------------------------\n')
        file.write(';########################################################################################################################\n')
        file.write('[doc_4]\n')
        file.write('; Приборы учета (ПУ) \n')
        file.write('name=pu\n\n')

        file.write('[pu_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[pu_1]\n')
        file.write('; Внутренний идентификатор ПУ\n')
        file.write('name=internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        if not (len(lines['1a'])==0 and len(lines['2a'])==0):
            file.write('offset_col_config=20\n')
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'offset_pattern=@{name}\n')
        else:
            file.write('row_data=0\n')
        file.write(f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУ,spacerepl,hash\n\n')
        for i, line in enumerate(l[1:]):
            file.write(f'[pu_1_{i}]\n')
            if not (len(lines['1a'])==0 and len(lines['2a'])==0):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            file.write(f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+ПУ,spacerepl,hash\n\n')

        file.write('[pu_2]\n')
        file.write('; Внутренний идентификатор ЛС\n')
        file.write('name=account_internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=id,spacerepl,hash\n\n')

        file.write('[pu_3]\n')
        file.write('; ГИС. Идентификатор ПУ GUID\n')
        file.write('name=gis_id\n\n')

        file.write('[pu_4]\n')
        file.write('; Серийный номер\n')
        file.write('name=serial_number\n\n')

        file.write('[pu_5]\n')
        file.write('; Тип устройства\n')
        file.write('name=device_type\n\n')

        file.write('[pu_6]\n')
        file.write('; Производитель\n')
        file.write('name=manufacturer\n\n')

        file.write('[pu_7]\n')
        file.write('; Модель\n')
        file.write('name=model\n\n')

        file.write('[pu_8]\n')
        file.write('; Показания момент установки. Тариф 1\n')
        file.write('name=rr1\n\n')

        file.write('[pu_9]\n')
        file.write('; Показания момент установки. Тариф 2\n')
        file.write('name=rr2\n\n')

        file.write('[pu_10]\n')
        file.write('; Показания момент установки. Тариф 3\n')
        file.write('name=rr3\n\n')

        file.write('[pu_11]\n')
        file.write('; Дата установки\n')
        file.write('name=installation_date\n\n')

        file.write('[pu_12]\n')
        file.write('; Дата начала работы\n')
        file.write('name=commissioning_date\n\n')

        file.write('[pu_13]\n')
        file.write('; Дата следующей поверки\n')
        file.write('name=next_verification_date\n\n')

        file.write('[pu_14]\n')
        file.write('; Дата последней поверки\n')
        file.write('name=first_verification_date\n\n')

        file.write('[pu_15]\n')
        file.write('; Дата опломбирования\n')
        file.write('name=factory_seal_date\n\n')

        file.write('[pu_16]\n')
        file.write('; Интервал проверки (кол-во месяцев)\n')
        file.write('name=checking_interval\n\n')

        file.write('[pu_17]\n')
        file.write('; Идентификатор услуги\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=service_internal_id\n')
        file.write('pattern=.+\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write(f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash\n\n')
        for i, line in enumerate(l[1:]):
            file.write(f'[pu_17_{i}]\n')
            file.write('; Идентификатор услуги\n')
            file.write(f'; {line["name"].rstrip()}\n')
            file.write(f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash\n\n')
    return file_name