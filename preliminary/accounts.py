def accounts(lines: list, path: str) -> str:

    file_name = f'{path}/ini/2_accounts.ini'
    with open(file_name, 'w') as file:
        file.write(
            ';########################################################################################################################\n')
        file.write(
            ';----------------------------------------------  Документы --------------------------------------------------------------\n')
        file.write(';########################################################################################################################\n\n')
        file.write(
            ';########################################################################################################################\n')
        file.write(';-------------------------------------------------------------- accounts -------------------------------------------------\n')
        file.write(
            ';########################################################################################################################\n')
        file.write('[doc_0]\n')
        file.write('; Лицевые счета\n')
        file.write('name=accounts\n')
        file.write('required_fields=internal_id\n\n')

        file.write('[accounts_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[accounts_1]\n')
        file.write('; Внутренний идентификатор договора\n')
        file.write('name=contract_internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=id+К,spacerepl,hash\n\n')

        file.write('[accounts_2]\n')
        file.write('; Внутренний идентификатор ЛС\n')
        file.write('name=internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=id,spacerepl,hash\n\n')

        file.write('[accounts_3]\n')
        file.write('; Идентификатор дома GUID\n')
        file.write('name=fias\n\n')

        file.write('[accounts_4]\n')
        file.write('; Адрес дома\n')
        file.write('name=address\n')
        file.write('pattern=.+\n')
        file.write('col_config=6\n')
        file.write('row_data=0\n')
        file.write('func=_+кв.+column_value(7)\n\n')

        file.write('[accounts_5]\n')
        file.write('; Номер помещения (если есть)\n')
        file.write('name=room_number\n')
        file.write('pattern=.+\n')
        file.write('col_config=7\n')
        file.write('row_data=0\n\n')

        file.write('[accounts_6]\n')
        file.write('; ГИС. Идентификатор квартиры GUID\n')
        file.write('name=gis_premises_id\n\n')

        file.write('[accounts_7]\n')
        file.write('; ГИС. Идентификатор блока GUID\n')
        file.write('name=gis_block_id\n\n')

        file.write('[accounts_8]\n')
        file.write('; ГИС. Идентификатор комнаты GUID\n')
        file.write('name=gis_room_id\n\n')

        file.write('[accounts_9]\n')
        file.write('; ГИС. Идентификатор ЛС GUID\n')
        file.write('name=gis_account_id\n\n')

        file.write('[accounts_10]\n')
        file.write('; Номер ЛС\n')
        file.write('name=account_number\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n\n')
        file.write('func=spacerepl\n\n')

        file.write('[accounts_11]\n')
        file.write('; ГИС. Идентификатор ЛС (20)\n')
        file.write('name=gis_account_service_id\n\n')

        file.write('[accounts_12]\n')
        file.write('; ГИС. Номер ЛИ (20)\n')
        file.write('name=gis_account_unified_number\n\n')

        file.write('[accounts_13]\n')
        file.write('; Общая площадь помещения\n')
        file.write('name=total_square\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('offset_col_config=9\n')
        file.write('offset_pattern=@currency\n\n')

        file.write('[accounts_14]\n')
        file.write('; Жилая площадь\n')
        file.write('name=residential_square\n\n')

        file.write('[accounts_15]\n')
        file.write('; Кол-во проживающих\n')
        file.write('name=living_person_number\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('offset_col_config=8\n')
        file.write('offset_pattern=.+\n\n')

        file.write('[accounts_16]\n')
        file.write('; Часовой пояс. Кол-во часов + или - от UTC\n')
        file.write('name=timezone\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=timezone\n\n')

        file.write('[accounts_17]\n')
        file.write(
            '; Альтернативный идентификатор ЛС, используется в некоторых конфигурациях.\n')
        file.write(
            '; Если  internal_id, по каким-то причинам не получается использовать.\n')
        file.write('name=account_identifier\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n\n')
        file.write('func=spacerepl\n\n')

        file.write('[accounts_18]\n')
        file.write('; Признак нежилого помещения (0 1)\n')
        file.write('name=not_residential\n\n')
    return file_name
