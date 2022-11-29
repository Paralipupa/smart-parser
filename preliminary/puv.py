from settings import *

def puv(lines:list, path: str):

    with open(f'{path}/ini/4_puv.ini', 'w') as file:
        file.write(';########################################################################################################################\n')
        file.write(';-------------------------------------------------------------- puv -----------------------------------------------------\n')
        file.write(';########################################################################################################################\n')
        file.write('[doc_4]\n')
        file.write('; ПУ показания\n')
        file.write('name=puv\n')
        file.write('required_fields=rr1,rr2,rr3\n\n')

        file.write('[puv_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[puv_1]\n')
        file.write('; Внутренний идентификатор ПУП\n')
        file.write('name=internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('offset_col_config=0\n')
        file.write('offset_pattern=.+\n')
        if len(lines["2"]) > 0:
            file.write(f'func=id+{lines["2"][0]["name"].replace(","," ").replace("+","")},spacerepl,hash\n\n')
            for i, line in enumerate(lines["2"][1:]):
                file.write(f'[puv_1_{i}]\n')
                file.write('; Внутренний идентификатор ПУП\n')
                file.write(f'func=id+{line["name"].replace(","," ").replace("+","").rstrip()},spacerepl,hash\n\n')
        else:
            file.write(f'func=id,spacerepl,hash\n\n')

        file.write('[puv_2]\n')
        file.write('; ГИС. Идентификатор ПУП GUID\n')
        file.write('name=gis_id\n\n')

        file.write('[puv_3]\n')
        file.write('; Внутренний идентификатор ПУ\n')
        file.write('name=metering_device_internal_id\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('offset_col_config=0\n')
        file.write('offset_pattern=.+\n')
        if len(lines["2"]) > 0:
            file.write(f'func=id+{lines["2"][0]["name"].replace(","," ").replace("+","")},spacerepl,hash\n\n')
            for i, line in enumerate(lines["2"][1:]):
                file.write(f'[puv_3_{i}]\n')
                file.write('; Внутренний идентификатор ПУ\n')
                file.write(f'func=id+{line["name"].replace(","," ").replace("+","").rstrip()},spacerepl,hash\n\n')
        else:
            file.write(f'func=id,spacerepl,hash\n\n')

        file.write('[puv_4]\n')
        file.write('; Дата\n')
        file.write('name=date\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=\n')
        file.write('func=period_last\n\n')

        file.write('[puv_5]\n')
        file.write('; Показание 1\n')
        file.write('name=rr1\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write(f'offset_col_config={COLUMN_BEGIN}\n')
        file.write('offset_pattern=.+\n')
        file.write('offset_type=float\n')
        file.write('func=round4\n\n')

        if len(lines["2"]) > 0:
            for i, line in enumerate(lines["2"][1:]):
                file.write(f'[puv_5_{i}]\n')
                file.write('; Показание 1\n')
                file.write(f'offset_col_config={COLUMN_BEGIN+1+i}\n\n')

        file.write('[puv_6]\n')
        file.write('; Показание 2\n')
        file.write('name=rr2\n\n')

        file.write('[puv_7]\n')
        file.write('; Показание 3\n')
        file.write('name=rr3\n\n')



