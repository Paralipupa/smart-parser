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
        file.write('name=pu\n')
        file.write('required_fields=internal_id,device_type,serial_number\n')
        file.write('\n')

        file.write('[pu_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n')
        file.write('\n')

        file.write('[pu_1]\n')
        file.write('; Внутренний идентификатор ПУ\n')
        file.write('name=internal_id\n')
        if lines["dic"].get("rr1"):
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            file.write(f'func=id+ХВС+ПУ,spacerepl,hash\n')
            file.write('\n')
            file.write(f'[pu_1_0]\n')
            file.write(f'func=id+ГВС+ПУ,spacerepl,hash\n')
            file.write('\n')
            file.write(f'[pu_1_1]\n')
            file.write(f'func=id+ЭЭ+ПУ,spacerepl,hash\n')
            file.write('\n')
            file.write(f'[pu_1_2]\n')
            file.write(f'func=id+ГАЗ+ПУ,spacerepl,hash\n')
            file.write('\n')
        file.write('\n')

        file.write('[pu_2]\n')
        file.write("; Внутренний идентификатор ЛС\n")
        file.write("name=account_internal_id\n")
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        if lines["dic"].get("account_internal_id"):
            file.write(
                f'offset_col_config={lines["dic"]["account_internal_id"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write("func=spacerepl,hash\n")
        file.write("\n")

        file.write('[pu_3]\n')
        file.write('; ГИС. Идентификатор ПУ GUID\n')
        file.write('name=gis_id\n')
        file.write('\n')

        file.write('[pu_4]\n')
        file.write('; Серийный номер\n')
        file.write('name=serial_number\n')
        if lines["dic"].get("serial_number"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["serial_number"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_5]\n')
        file.write('; Тип устройства\n')
        file.write('name=device_type\n')
        if lines["dic"].get("device_type"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["device_type"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_6]\n')
        file.write('; Производитель\n')
        file.write('name=manufacturer\n')
        if lines["dic"].get("manufacturer"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["manufacturer"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_7]\n')
        file.write('; Модель\n')
        file.write('name=model\n')
        if lines["dic"].get("model"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["model"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_8]\n')
        file.write('; Показания момент установки. Тариф 1\n')
        file.write('name=rr1\n')
        if lines["dic"].get("pu_rr1"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["pu_rr1"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_9]\n')
        file.write('; Показания момент установки. Тариф 2\n')
        file.write('name=rr2\n')
        if lines["dic"].get("pu_rr2"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["pu_rr2"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_10]\n')
        file.write('; Показания момент установки. Тариф 3\n')
        file.write('name=rr3\n')
        if lines["dic"].get("pu_rr3"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["pu_rr3"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_11]\n')
        file.write('; Дата установки\n')
        file.write('name=installation_date\n')
        if lines["dic"].get("installation_date"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["installation_date"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_12]\n')
        file.write('; Дата начала работы\n')
        file.write('name=commissioning_date\n')
        if lines["dic"].get("commissioning_date"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["commissioning_date"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_13]\n')
        file.write('; Дата следующей поверки\n')
        file.write('name=next_verification_date\n')
        if lines["dic"].get("next_verification_date"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["next_verification_date"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_14]\n')
        file.write('; Дата последней поверки\n')
        file.write('name=first_verification_date\n')
        if lines["dic"].get("first_verification_date"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["first_verification_date"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_15]\n')
        file.write('; Дата опломбирования\n')
        file.write('name=factory_seal_date\n')
        if lines["dic"].get("factory_seal_date"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["factory_seal_date"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_16]\n')
        file.write('; Интервал проверки (кол-во месяцев)\n')
        file.write('name=checking_interval\n')
        if lines["dic"].get("checking_interval"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["checking_interval"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write('\n')

        file.write('[pu_17]\n')
        file.write('; Идентификатор услуги\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=service_internal_id\n')
        if lines["dic"].get("rr1"):
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            file.write(f'func=id+ХВС,spacerepl\n')
            file.write('\n')
            file.write(f'[pu_17_0]\n')
            file.write(f'func=id+ГВС,spacerepl\n')
            file.write('\n')
            file.write(f'[pu_17_1]\n')
            file.write(f'func=id+ЭЭ,spacerepl\n')
            file.write('\n')
            file.write(f'[pu_17_2]\n')
            file.write(f'func=id+ГАЗ,spacerepl\n')
            file.write('\n')
        file.write('\n')

        
    return file_name