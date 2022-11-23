def pp_charges(lines:list, path: str):

    with open(f'{path}/pp_charges.ini', 'w') as file:
        file.write(';--------- pp_charges -----------\n')
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
        file.write('offset_col_config=0\n')
        file.write('offset_pattern=.+\n')
        file.write(f'func=id+{lines[0].replace(","," ").replace("+","")},spacerepl,hash\n\n')
        for i, line in enumerate(lines[1:]):
            file.write(f'[pp_charges_1_{i}]\n')
            file.write(f'func=id+{line.replace(","," ").replace("+","").rstrip()},spacerepl,hash\n\n')

        file.write('[pp_charges_2]\n')
        file.write('; Внутренний идентификатор платежного документа\n')
        file.write('name=pp_internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=id+ПД,spacerepl,hash\n\n')

        file.write('[pp_charges_3]\n')
        file.write('; Сумма начисления при однотарифном начислении\n')
        file.write(f'; {lines[0]}\n')
        file.write('name=calc_value\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('offset_col_config=10\n')
        file.write('offset_pattern=@currency\n')
        file.write('offset_type=float\n\n')
        for i, line in enumerate(lines[1:]):
            file.write(f'[pp_charges_3_{i}]\n')
            file.write('; Сумма начисления при однотарифном начислении\n')
            file.write(f'; {line.rstrip()}\n')
            file.write(f'offset_col_config={11+i}\n\n')

        file.write('[pp_charges_4]\n')
        file.write('; тариф при однотарифном начислении (поля: ГВС, ХВС)\n')
        file.write('name=tariff\n\n')

        file.write('[pp_charges_5]\n')
        file.write('; Идентификатор услуги\n')
        file.write(f'; {lines[0]}\n')
        file.write('name=service_internal_id\n')
        file.write('pattern=.+\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=1,hash\n\n')
        for i, line in enumerate(lines[1:]):
            file.write(f'[pp_charges_5_{i}]\n')
            file.write('; Идентификатор услуги\n')
            file.write(f'; {line.rstrip()}\n')
            file.write(f'func={2+i},hash\n\n')

        file.write('[pp_charges_6]\n')
        file.write('; кол-во услуги  при однотарифном начислении\n')
        file.write('name=rr\n\n')

        file.write('[pp_charges_7]\n')
        file.write('; перерасчет\n')
        file.write('name=recalculation\n\n')

        file.write('[pp_charges_8]\n')
        file.write('; Начислено за расчетный период,с  учетом перерасчета\n')
        file.write(f'; {lines[0]}\n')
        file.write('name=accounting_period_total\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('offset_col_config=10\n')
        file.write('offset_pattern=@currency\n')
        file.write('offset_type=float\n\n')
        for i, line in enumerate(lines[1:]):
            file.write(f'[pp_charges_8_{i}]\n')
            file.write('; Начислено за расчетный период,с  учетом перерасчета\n')
            file.write(f'; {line.rstrip()}\n')
            file.write(f'offset_col_config={11+i}\n\n')


