def pp_service(lines:list, path: str):

    with open(f'{path}/5_pp_service.ini', 'w') as file:
        file.write(';--------- pp_service -----------\n')
        file.write('[doc_3]\n')
        file.write(';Документ. Услуги (pp_service.csv)\n')
        file.write('name=pp_service\n\n')

        file.write('[pp_service_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[pp_service_1]\n')
        file.write('; Внутренний идентификатор услуги \n')
        file.write(f'; {lines[0]}\n')
        file.write('name=internal_id\n')
        file.write('pattern=.+\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=1,hash\n\n')

        for i, line in enumerate(lines[1:]):
            file.write(f'[pp_service_1_{i}]\n')
            file.write('; Внутренний идентификатор услуги\n')
            file.write(f'; {line.rstrip()}\n')
            file.write(f'func={i+2},hash\n\n')

        for k in [2,3]:
            file.write(f'[pp_service_{k}]\n')
            if k == 2:
                file.write('; наименование в 1с\n')
                file.write('; Строка 200\n')
                file.write('name=name\n')
            else:
                file.write('; вид в 1с (полное наименование)\n')
                file.write('; Строка 200\n')
                file.write('name=kindoffset\n')
            file.write('pattern=.+\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            file.write(f'func={lines[0].replace(","," ").replace("+","")}\n\n')
            for i, line in enumerate(lines[1:]):
                file.write(f'[pp_service_{k}_{i}]\n')
                file.write(f'func={line.replace(","," ").replace("+","").rstrip()}\n\n')

        file.write('[pp_service_4]\n')
        file.write('; код услуги в ГИС\n')	
        file.write('name=gis_code\n')
