import re
from utils import get_ident, get_reg, get_name
from settings import *

def pp_charges(lines:list, path: str):    
    names = []
    l = []
    if len(lines['1a'])==0 and len(lines['2a'])==0:
        l.extend(lines['1'])
        l.extend(lines['2'])
    else:
        l.extend(lines['1a'])
        l.extend(lines['2a'])
    ll = l[-1:]
    l = sorted(l[:-1], key=lambda x: x['name'])
    l.extend(ll)

    with open(f'{path}/ini/4_pp_charges.ini', 'w') as file:
        file.write(';########################################################################################################################\n')
        file.write(';-------------------------------------------------------------- pp_charges ----------------------------------------------\n')
        file.write(';########################################################################################################################\n')
        file.write('[doc_2]\n')
        file.write('; Документ Начисления платежей\n')
        file.write('name=pp_charges\n')
        file.write('required_fields=calc_value\n\n')

        file.write('[pp_charges_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[pp_charges_1]\n')
        file.write('; Внутренний идентификатор начисления\n')
        file.write('name=internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        if not (len(lines['1a'])==0 and len(lines['2a'])==0):
            file.write('offset_col_config=20\n')
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'offset_pattern=@{name}\n')
        else:
            file.write('row_data=0\n')
        file.write(f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+НЧ,spacerepl,hash\n\n')
        for i, line in enumerate(l[1:]):
            file.write(f'[pp_charges_1_{i}]\n')
            if not (len(lines['1a'])==0 and len(lines['2a'])==0):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            file.write(f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+НЧ,spacerepl,hash\n\n')

        file.write('[pp_charges_2]\n')
        file.write('; Внутренний идентификатор платежного документа\n')
        file.write('name=pp_internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=id+ПД,spacerepl,hash\n\n')

        names = []
        file.write('[pp_charges_3]\n')
        file.write('; Сумма начисления при однотарифном начислении\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=calc_value\n')
        if not (len(lines['1a'])==0 and len(lines['2a'])==0):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'pattern=@{name}\n')
            file.write('col_config=20\n')
            file.write(f'offset_col_config=2\n')
        else:
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            file.write(f'offset_col_config={COLUMN_BEGIN}\n')
        file.write('offset_pattern=@currency\n')
        file.write('offset_type=float\n\n')
        for i, line in enumerate(l[1:]):
            file.write(f'[pp_charges_3_{i}]\n')
            file.write('; Сумма начисления при однотарифном начислении\n')
            file.write(f'; {line["name"].rstrip()}\n')
            if not (len(lines['1a'])==0 and len(lines['2a'])==0):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n\n')
            else:
                file.write(f'offset_col_config={COLUMN_BEGIN+1+i}\n\n')

        names = []
        file.write('[pp_charges_4]\n')
        file.write('; тариф при однотарифном начислении\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=tariff\n')
        if not (len(lines['1a'])==0 and len(lines['2a'])==0):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'pattern=@{name}\n')
            file.write('col_config=20\n')
            file.write(f'offset_col_config=21\n')
            file.write('offset_pattern=@currency\n\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[pp_charges_4_{i}]\n')
                file.write('; тариф при однотарифном начислении\n')
                file.write(f'; {line["name"].rstrip()}\n')
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n\n')
        else:
            file.write('pattern=.+\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            file.write(f'func=fias+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash,dictionary\n\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[pp_charges_4_{i}]\n')
                file.write('; тариф при однотарифном начислении\n')
                file.write(f'; {line["name"].rstrip()}\n')
                file.write(f'func=fias+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash,dictionary\n\n')


        names = []
        file.write('[pp_charges_5]\n')
        file.write('; Идентификатор услуги\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=service_internal_id\n')
        file.write('pattern=.+\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write(f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash\n\n')
        for i, line in enumerate(l[1:]):
            file.write(f'[pp_charges_5_{i}]\n')
            file.write('; Идентификатор услуги\n')
            file.write(f'; {line["name"].rstrip()}\n')
            file.write(f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash\n\n')

        file.write('[pp_charges_6]\n')
        file.write('; кол-во услуги  при однотарифном начислении\n')
        file.write('name=rr\n\n')

        names = []
        file.write('[pp_charges_7]\n')
        file.write('; перерасчет\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=recalculation\n')
        if not (len(lines['1a'])==0 and len(lines['2a'])==0):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'pattern=@{name}\n')
            file.write('col_config=20\n')
            file.write(f'offset_col_config=23\n')
            file.write('offset_pattern=@currency\n\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[pp_charges_7_{i}]\n')
                file.write('; тариф при однотарифном начислении\n')
                file.write(f'; {line["name"].rstrip()}\n')
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n\n')

        names = []
        file.write('[pp_charges_8]\n')
        file.write('; Начислено за расчетный период,с  учетом перерасчета\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=accounting_period_total\n')
        if not (len(lines['1a'])==0 and len(lines['2a'])==0):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f'pattern=@{name}\n')
            file.write('col_config=20\n')
            file.write(f'offset_col_config=2\n')
        else:
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            file.write(f'offset_col_config={COLUMN_BEGIN}\n')
        file.write('offset_pattern=@currency\n')
        file.write('offset_type=float\n\n')
        for i, line in enumerate(l[1:]):
            file.write(f'[pp_charges_8_{i}]\n')
            file.write('; Сумма начисления при однотарифном начислении\n')
            file.write(f'; {line["name"].rstrip()}\n')
            if not (len(lines['1a'])==0 and len(lines['2a'])==0):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n\n')
            else:
                file.write(f'offset_col_config={COLUMN_BEGIN+1+i}\n\n')


