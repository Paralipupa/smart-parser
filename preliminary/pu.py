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
        file.write('required_fields=internal_id\n')
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
            if lines["dic"].get("service"):
                file.write(f'offset_col_config={lines["dic"]["service"][0]["col"]}\n')
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            else:
                file.write('row_data=0\n')
            if lines["dic"].get("internal_id_pu"):
                file.write(f'func=id+{get_ident(lines["dic"]["internal_id_pu"][0]["name"])}+ПУ,spacerepl,hash\n')
            else:
                file.write(f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУ,spacerepl,hash\n')
            file.write('\n')
            if lines["dic"].get("internal_id_pu"):
                for i, line in enumerate(lines["dic"]["internal_id_pu"][1:]):
                    file.write(f'[pu_1_{i}]\n')
                    file.write('; Внутренний идентификатор ПУ\n')
                    file.write(f'func=id+{get_ident(line["name"])}+ПУ,spacerepl,hash\n')
            else:
                for i, line in enumerate(l[1:]):
                    file.write(f'[pu_1_{i}]\n')
                    file.write('; Внутренний идентификатор ПУ\n')
                    if lines["dic"].get("service"):
                        name = get_name(get_ident(line["name"].split(";")[0]), names)
                        file.write(f'offset_pattern=@{name}\n')
                    file.write(f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+ПУ,spacerepl,hash\n')
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
            for i, line in enumerate(lines["dic"]["serial_number"][1:]):
                file.write(f'[pu_4_{i}]\n')
                file.write('; Серийный номер\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["device_type"][1:]):
                file.write(f'[pu_5_{i}]\n')
                file.write('; Тип устройства\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["manufacturer"][1:]):
                file.write(f'[pu_6_{i}]\n')
                file.write('; Производитель\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["model"][1:]):
                file.write(f'[pu_7_{i}]\n')
                file.write('; Модель\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
        file.write('\n')

        file.write('[pu_8]\n')
        file.write('; Показания момент установки. Тариф 1\n')
        file.write('name=rr1\n')
        if lines["dic"].get("rr1_pu"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["rr1_pu"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
            for i, line in enumerate(lines["dic"]["rr1_pu"][1:]):
                file.write(f'[pu_8_{i}]\n')
                file.write('; Показания момент установки. Тариф 1\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
        file.write('\n')

        file.write('[pu_9]\n')
        file.write('; Показания момент установки. Тариф 2\n')
        file.write('name=rr2\n')
        if lines["dic"].get("rr2_pu"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["rr2_pu"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
            for i, line in enumerate(lines["dic"]["rr2_pu"][1:]):
                file.write(f'[pu_9_{i}]\n')
                file.write('; Показания момент установки. Тариф 2\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
        file.write('\n')

        file.write('[pu_10]\n')
        file.write('; Показания момент установки. Тариф 3\n')
        file.write('name=rr3\n')
        if lines["dic"].get("rr3_pu"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["rr3_pu"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
            for i, line in enumerate(lines["dic"]["rr3_pu"][1:]):
                file.write(f'[pu_10_{i}]\n')
                file.write('; Показания момент установки. Тариф 3\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["installation_date"][1:]):
                file.write(f'[pu_11_{i}]\n')
                file.write('; Дата установки\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["commissioning_date"][1:]):
                file.write(f'[pu_12_{i}]\n')
                file.write('; Дата начала работы\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["next_verification_date"][1:]):
                file.write(f'[pu_13_{i}]\n')
                file.write('; Дата следующей поверки\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["first_verification_date"][1:]):
                file.write(f'[pu_14_{i}]\n')
                file.write('; Дата последней поверки\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["factory_seal_date"][1:]):
                file.write(f'[pu_15_{i}]\n')
                file.write('; Дата опломбирования\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
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
            for i, line in enumerate(lines["dic"]["checking_interval"][1:]):
                file.write(f'[pu_16_{i}]\n')
                file.write('; Интервал проверки (кол-во месяцев)\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
        file.write('\n')

        file.write('[pu_17]\n')
        file.write('; Идентификатор услуги\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=service_internal_id\n')
        if lines["dic"].get("rr1"):
            file.write('pattern=.+\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            if lines["dic"].get("internal_id_pu"):
                file.write(f'func={get_ident(lines["dic"]["internal_id_pu"][0]["name"])},spacerepl,hash\n')
            else:
                file.write(f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash\n')
            file.write('\n')
            if lines["dic"].get("internal_id_pu"):
                for i, line in enumerate(lines["dic"]["internal_id_pu"][1:]):
                    file.write(f'[pu_17_{i}]\n')
                    file.write('; Идентификатор услуги\n')
                    file.write(f'func={get_ident(line["name"])},spacerepl,hash\n')
            else:
                for i, line in enumerate(l[1:]):
                    file.write(f'[pu_17_{i}]\n')
                    file.write('; Идентификатор услуги\n')
                    file.write(f'; {line["name"].rstrip()}\n')
                    file.write(f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash\n')
        file.write('\n')
        

    return file_name