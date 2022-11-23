def pp(lines:list, path: str):

    with open(f'{path}/pp.ini', 'w') as file:
        file.write('[doc_]\n')
        file.write('; Документ \n')
        file.write('name=pp\n')
        file.write('required_fields=bill_value\n\n')
        file.write('[pp_0]
        file.write(';ИНН, ОГРН или OrgID
        file.write('name=org_ppa_guid
        file.write('pattern=@
        file.write('col_config=0
        file.write('row_data=0
        file.write('func=inn

        file.write('[pp_1]
        file.write('; Внутренний идентификатор ПД
        file.write('name=internal_id
        file.write('pattern=@0
        file.write('col_config=0
        file.write('row_data=0
        file.write('func=id+ПД,spacerepl,hash

        file.write('[pp_2]
        file.write('; Внутренний идентификатор ЛС
        file.write('name=account_internal_id
        file.write('pattern=@0
        file.write('col_config=0
        file.write('row_data=0
        file.write('func=spacerepl,hash

        file.write('[pp_3]
        file.write('; ГИС. Идентификатор ПП
        file.write('name=gis_id

        file.write('[pp_4]
        file.write('; Месяц (первый день месяца)round2
        file.write('name=month
        file.write('pattern=@0
        col_config=0
        row_data=0
        func=period

        [pp_5]
        ; Сальдо на начало месяца (<0 переплата, >0 задолженность)
        name=credit
        pattern=@0
        col_config=0
        offset_col_config=1
        offset_type=float
        offset_pattern=@currency
        func=round2

        [pp_6]
        ; Сальдо на конец месяца (<0 переплата, >0 задолженность)
        name=saldo
        pattern=@0
        col_config=0
        offset_col_config=4
        offset_type=float
        offset_pattern=@currency
        func=round2

        [pp_7]
        ; Оплачено денежных средств в расчетный период
        name=payment_value
        pattern=@0
        col_config=0
        offset_col_config=3
        offset_type=float
        offset_pattern=@currency

        [pp_8]
        ; Учтены платежи, поступившие до указанного числа расчетного периода включительно
        name=payment_date
        pattern=@0
        col_config=0
        row_data=0
        func=period_last
        depends_on=payment_value

        [pp_9]
        ; Сумма счета, учетом задолженности/переплаты
        name=bill_value
        pattern=@0
        col_config=0
        offset_col_config=2
        offset_type=float
        offset_pattern=@currency
        func=round2

        [pp_10]
        ; Номер расчетного счета
        name=account_number

        [pp_11]
        ; БИК банка
        name=bank_bik



        # file.write('[pp_0]
        # file.write(';ИНН, ОГРН или OrgID
        # file.write('name=org_ppa_guid
        # file.write('pattern=@
        # file.write('col_config=0
        # file.write('row_data=0
        # file.write('func=inn

        # file.write('[pp_1]
        # file.write('; Внутренний идентификатор ПД
        # file.write('name=internal_id
        # file.write('pattern=@0
        # file.write('col_config=0
        # file.write('row_data=0
        # file.write('func=id+ПД,spacerepl,hash

        # file.write('[pp_2]
        # file.write('; Внутренний идентификатор ЛС
        # file.write('name=account_internal_id
        # file.write('pattern=@0
        # file.write('col_config=0
        # file.write('row_data=0
        # file.write('func=spacerepl,hash

        # file.write('[pp_3]
        # file.write('; ГИС. Идентификатор ПП
        # file.write('name=gis_id

        # file.write('[pp_4]
        # file.write('; Месяц (первый день месяца)round2
        # file.write('name=month
        # file.write('pattern=@0
        # col_config=0
        # row_data=0
        # func=period

        # [pp_5]
        # ; Сальдо на начало месяца (<0 переплата, >0 задолженность)
        # name=credit
        # pattern=@0
        # col_config=0
        # offset_col_config=1
        # offset_type=float
        # offset_pattern=@currency
        # func=round2

        # [pp_6]
        # ; Сальдо на конец месяца (<0 переплата, >0 задолженность)
        # name=saldo
        # pattern=@0
        # col_config=0
        # offset_col_config=4
        # offset_type=float
        # offset_pattern=@currency
        # func=round2

        # [pp_7]
        # ; Оплачено денежных средств в расчетный период
        # name=payment_value
        # pattern=@0
        # col_config=0
        # offset_col_config=3
        # offset_type=float
        # offset_pattern=@currency

        # [pp_8]
        # ; Учтены платежи, поступившие до указанного числа расчетного периода включительно
        # name=payment_date
        # pattern=@0
        # col_config=0
        # row_data=0
        # func=period_last
        # depends_on=payment_value

        # [pp_9]
        # ; Сумма счета, учетом задолженности/переплаты
        # name=bill_value
        # pattern=@0
        # col_config=0
        # offset_col_config=2
        # offset_type=float
        # offset_pattern=@currency
        # func=round2

        # [pp_10]
        # ; Номер расчетного счета
        # name=account_number

        # [pp_11]
        # ; БИК банка
        # name=bank_bik


