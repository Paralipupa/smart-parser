def pp(lines:list, path: str):
    file_name = f'{path}/ini/3_pp.ini'
    with open(file_name, 'w') as file:
        file.write(';########################################################################################################################\n')
        file.write(';---------------------------------------------------------------- pp ----------------------------------------------------\n')
        file.write(';########################################################################################################################\n')
        file.write('[doc_1]\n')
        file.write('; Платежный документ \n')
        file.write('name=pp\n')
        file.write('required_fields=bill_value,payment_value\n\n')

        file.write('[pp_0]\n')
        file.write(';ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[pp_1]\n')
        file.write('; Внутренний идентификатор ПД\n')
        file.write('name=internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=id+ПД,spacerepl,hash\n\n')

        file.write('[pp_2]\n')
        file.write('; Внутренний идентификатор ЛС\n')
        file.write('name=account_internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=spacerepl,hash\n\n')

        file.write('[pp_3]\n')
        file.write('; ГИС. Идентификатор ПП\n')
        file.write('name=gis_id\n\n')

        file.write('[pp_4]\n')
        file.write('; Месяц (первый день месяца)\n')
        file.write('name=month\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=period_first\n\n')

        file.write('[pp_5]\n')
        file.write('; Сальдо на начало месяца (<0 переплата, >0 задолженность)\n')
        file.write('name=credit\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write(f'offset_col_config={lines["dic"].get("credit", {"col":1})["col"]}\n')
        file.write('offset_type=float\n')
        file.write('offset_pattern=@currency\n')
        file.write('func=round2\n\n')

        file.write('[pp_6]\n')
        file.write('; Сальдо на конец месяца (<0 переплата, >0 задолженность)\n')
        file.write('name=saldo\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write(f'offset_col_config={lines["dic"].get("saldo", {"col":4})["col"]}\n')
        file.write('offset_type=float\n')
        file.write('offset_pattern=@currency\n')
        file.write('func=round2\n\n')

        file.write('[pp_7]\n')
        file.write('; Оплачено денежных средств в расчетный период\n')
        file.write('name=payment_value\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write(f'offset_col_config={lines["dic"].get("payment_value", {"col":3})["col"]}\n')
        file.write('offset_type=float\n')
        file.write('offset_pattern=@currency\n')
        file.write('func=round2\n\n')

        file.write('[pp_8]\n')
        file.write('; Учтены платежи, поступившие до указанного числа расчетного периода включительно\n')
        file.write('name=payment_date\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        if lines["dic"].get("payment_date"):
            file.write(f'offset_col_config={lines["dic"].get("payment_date", {"col":5})["col"]}\n')
            file.write('offset_pattern=.+\n')
        else:
            file.write('func=period_last\n')
        file.write('depends_on=payment_value\n')
        file.write('\n')

        file.write('[pp_9]\n')
        file.write('; Сумма счета, учетом задолженности/переплаты\n')
        file.write('name=bill_value\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write(f'offset_col_config={lines["dic"].get("bill_value", {"col":2})["col"]}\n')
        file.write('offset_type=float\n')
        file.write('offset_pattern=@currency\n')
        file.write('func=round2\n\n')

        file.write('[pp_10]\n')
        file.write('; Номер расчетного счета\n')
        file.write('name=account_number\n')
        if lines['param'].get('pattern_account_number',''):
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n') 
            file.write(f'offset_col_config=0\n')
            file.write('offset_pattern=@0\n')
            file.write(f"func={lines['param']['pattern_account_number'][0][1:]},spacerepl\n")    
            file.write('\n')
            for i, line in enumerate(lines['param']['pattern_account_number'][1:]):
                file.write(f'[pp_10_{i}]\n')
                file.write('; Номер расчетного счета\n')
                file.write(f"func={line[1:]},spacerepl\n")    
                file.write('\n')
        file.write('\n')

        file.write('[pp_11]\n')
        file.write('; БИК банка\n')
        file.write('name=bank_bik\n')
        if lines['param'].get('pattern_bik',''):
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n') 
            file.write(f'offset_col_config=0\n')
            file.write('offset_pattern=@0\n')
            file.write(f"func={lines['param']['pattern_bik'][0][1:]},spacerepl\n")    
            file.write('\n')
            for i, line in enumerate(lines['param']['pattern_bik'][1:]):
                file.write(f'[pp_11_{i}]\n')
                file.write('; БИК банка\n')
                file.write(f"func={line[1:]},spacerepl\n")    
                file.write('\n')
        file.write('\n')
        file.write('\n')

    return file_name

