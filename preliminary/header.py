def header(lines:list, path: str):

    with open(f'{path}/0_header.ini', 'w') as file:
        file.write(';---------------ТСЖ "Молодежное"----------------\n')
        file.write('[check]\n')
        file.write('; Поиск ключевого значения по строке(ам) для определения совместимости\n')
        file.write('; входных данных и конфигурации\n')
        file.write('row=0<15\n')
        file.write('pattern=Параметры\n')
        file.write('pattern_0=Отбор\n\n')

        file.write('[main]\n')
        file.write('path_output=output\n')
        file.write('row_start=0\n')
        file.write('page_name=\n')
        file.write('page_index=0\n')
        file.write('max_columns=150\n')
        file.write('max_rows_heading=20\n\n')

        file.write(';---- шаблоны регулярных выражений ------------\n\n')

        file.write('[pattern]\n')
        file.write('name=period\n')
        file.write('pattern=(?<=Начало периода: )[0-9]{2}\.{0-9}{2}\.[0-9]{4}\n\n')

        file.write('[pattern_0]\n')
        file.write('name=currency\n')
        file.write('pattern=^-?\d{1,5}(?:[\.,]\d{1,3})?$\n\n')

        file.write('[pattern_1]\n')
        file.write('name=ЛС\n')
        file.write('pattern=^[0-9]{1,6}-[0-9]+(?=,)\n')
        file.write('pattern_0=^[0-9]{1,6}(?=,)\n')
        file.write('pattern_1=^[0-9]{1,6}-П(?=,)\n\n')

        file.write(';---- параметры ------------\n\n')

        file.write('[headers_0]\n')
        file.write('name=period\n')
        file.write('row=0<5\n')
        file.write('column=0<5\n')
        file.write('pattern=@period\n\n')

        file.write('[headers_1]\n')
        file.write('name=inn\n')
        file.write('pattern=@4727000113\n\n')

        file.write('[headers_2]\n')
        file.write('name=timezone\n')
        file.write('pattern=@+3\n\n')
