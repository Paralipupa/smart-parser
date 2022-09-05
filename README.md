Парсинг xml в файл json|csv

Запуск:
  python main.py [--name|-n]=<file.lst>|<file.xsl>|<file.zip> [[--inn|-i]=<inn>] [[--config|-c]=<config.ini>] [[--union|-u]=<path>']

--name= задает имя исходного файла для обработки.
--config= файл конфигурации. При его отсутствии ищется в каталоге конфигураций по шаблону
--inn= ИНН. При отсутствии берется из имени файла.
--union= путь для объединения однотипных данных. Однотипными считаются имена файлов с совпадающими ИНН, периодом и типом.
Допустимые типы данных: accounts, pp, pp_charges, pp_service, pu, puv
В .lst задается список файлов по одному на каждую строку. Для отключения файла от обработки указывется
знак ";" в начале строки.

Выходные данные помещаются в папку output.  
Данные выводятся в формате: <инн>_<год>_<месяц>_<порядковый номер>_<тип данных>[.json|.csv]
Например: 00000000_2022_08_01_accounts.csv,00000000_2022_08_02_accounts.csv

При указании параметра --union= однотипные данные с разными порядковыми номерами объединяются и заносятся в новый файл
в формате: <инн>_<тип данных>_<год>_<месяц>[.json|.csv]
Например: 00000000_accounts_2022_08.csv


Разделы конфигурационного файла ini:

[check]
Раздел используется для проверки совместимости исходного файла xsl и конфигурации.

row=число|диапазон чисел            ;строки ячеек, для проверки значения
column=число|диапазон чисел         ;колонки ячеек, для проверки значения
pattern=регулярное выражение        ;поиск значения по всей строке для проверки совместимости файла и
                                     данной конфигурации
pattern_x=регулярное выражение      ;дополнительное условие поиска к pattern, где x - порядковый номер начиная от нуля
PS. диапазон чисел (здесь и далее)задается либо перечислением числовых значений через запятую,
например: 0,1,3,5; либо через указание интервала с использованием знака "<",
например: 0<4 что соответсвует 0,1,2,3,4

[header]
Раздел используется, если в файле более одной таблицы. Например "квитанции за декабрь 2021.xml"

row=число|диапазон чисел            ;строки ячеек, для проверки начала заголовочной области
                                    (перед табличными данными)
column=число|диапазон чисел         ;колонки ячеек, для проверки начала заголовочной области
pattern=регулярное выражение        ;поиск значения для проверки начала заголовочной области

[main]
path=строка                         ;путь выходного файла (по-умолчанию output в текущем каталоге)
row_start=
page_name=имя листа                 ;имя или имена через запятую листов в файле
page_index=номер листа              ;номер или номера листов в файле. Если задано имя, параметр игнорируется 
max_columns=число                   ;количество просматриваемых колонок для поиска заголовков таблицы
max_rows_heading=число              ;количество просматриваемых строк для поиска заголовков таблицы
rows_exclude=число|диапазон чисел   ;не обрабатываемые порядковые номера строк в табличной области

[pattern]
name=имя                            ;произвольное имя шаблона
pattern=шаблон                      ;регулярное выражение

[headers_x] ; x-число в диапазоне [0,]
Раздел используется для нахождения значений перед таблицей
Эти значения можно использовать в качестве параметров функции param(<имя>) (см.далее)

name=строка                         ;имя параметра, например - name=period
row=число|числа через запятую       ;номера строк ячеек, для поиска значения параметра
column=число|диапазон чисел         ;номера колонк ячеек, для поиска значения параметра
pattern=регулярное выражение        ;шаблон для поиска значения параметра
pattern_x=регулярное выражение      ;дополнительные условия проверки

Здесь и далее нумерация колонок и строк начинается то нуля.

[footers_x] ; x-число в диапазоне [0,]
Раздел используется, если в файле более одной таблицы. Например "квитанции за декабрь 2021.xml"
Назначение аналогично headers_x

name=строка                        ; имя параметра, например - name=itog
row=число|диапазон чисел           ;строки ячеек, для определения параметра
column=число|диапазон чисел        ;колонки ячеек, для определения параметра
pattern=регулярное выражение       ;поиск значения параметра
pattern_x=регулярное выражение     ;дополнительные условия проверки


[col_x] ; x-порядковый номер колонки в диапазоне [0,]
Раздел для определения колонок таблицы

name=строка                                 ;наименование (идентификатор) колонки
pattern=строка|регулярное выражение         ;поиск заголовка колонки таблицы
pattern_x=строка|регулярное выражение       ;дополнительные условия, если предыдущее не найдено
condition_begin_team=регулярное выражение   ; начала (области|иерархии) для разбиения данных таблицы по строкам
condition_end_table=регулярное выражение    ; поиск окончания табличных данных
col_data_offset=число|диапазон чисел        ; номера столбцов для добавления 
offset_pattern=строка|регулярное выражение  ; "якорь"(дополнительное уточнение) для заголовка колонки
offset_row=число|диапазон чисел             ; номера строк поиска "якоря" для заголовка данной колонки
offset_col=число|диапазон чисел             ; номера столбцов поиска "якоря" для заголовка данной колонки
border_column_left=число                    ; порядковый номер колонки в конфигурации ограничивающий слева
                                              поиск заголовка
border_column_right=число                    ; порядковый номер колонки в конфигурации ограничивающий справа
                                              поиск заголовка
is_optional=0|(1,true)                       ;признак необязательной колонки в таблице (по умолчанию
                                               0 - обязательная колонка)
is_duplicate=0|(1,true)                      ; признак того, что колонка исходной таблицы может повторятся
is_unique=0|(1,true)                         ; признак того, что в исходной таблице берется только 
                                              одно значение (остальные колонки в xls, найденные по шаблону
                                               игнорируются )
is_only_after_stable=0|1                     ; колонка ищется только после нахождения всех постоянных
                                               (optional=0) колонок (если задана, то для нее параметр 
                                               is_optional всегда 'true' )

PS. Если под условие заданное в pattern попадает несколько колонок таблицы (за исключением, когда is_unique=true), то данные по ним суммируются при числовых или конкатенируются при строковых значениях.
condition_begin_team и condition_end_table задаются в любой из колонок, где необходимо проверить условия.
При установки значений в нескольких колонках, берется условие из колонки с наименьшим номером, остальные
условия игнорируются.

[doc_x] ; x-порядковый номер документа в диапазоне [0,]
Раздел для настройки выходного документа

name=строка                                 ; наименование выходного документа, например: name=accounts
rows_exclude=число|диапазон чисел           ; не обрабатываемые порядковые номера строк в иерархической области
required_fields=имена полей через запятую   ; список обязательных для заполнения полей.
                                              Например: required_fields=r1,r2,r3. Обязательным является заполение
                                              хотя бы одного поля из списка. Если список не задан, то выходная запись формируется в случае заполнения любого из полей документа.


[имя_x] ; имя=name из раздела [doc_x], x-порядковый номер документа в диапазоне [0,], например [accounts_0]
Раздел определяет настройку имен полей выходного документа

name=строка                              ; имя поля
pattern=регулярное выражение|@[x]        ; шаблон для проверки значения данного поля
rows_exclude=число|диапазон чисел        ; не обрабатываемые номера строк для данного поля
col_config=число|диапазон чисел          ; номер(а) колонок для поиска по заданному шаблону
row_data=число|диапазон чисел            ; номер(а) строк в разбиваемой области (иерархии) таблицы, если пусто
                                          то берутся все строки из рассматриваемой области (иерархии)
type=int | float                         ; тип данных текущего поля. По-умолчанию - строковые значения
offset_col_config=число                  ; (смещение) порядковый номер колонки из конфигурации откуда
                                            берутся значения по найденному шаблону. Если не  заданно, то данные берутся из колонки, указаной в col_config
offset_row_data=число|числа через запятую  ; (смещение) порядковый номера строки в области (иерархии)
                                            откуда берутся значения по найденному шаблону
offset_pattern=регулярное выражение       ; шаблон для данных из колонки offset_col и offset_row_data
func=имя фунции или параметра             ;имена встроенных функций или заданых параметров из раздела headers для обработки полученного
                                           значения поля, например: func=id,uuid. При этом обработка данных происходит последовательно с передачей полученного значений в следующую функцию, указанную после запятой.
func_pattern=регулярное выражение         ; для проверки результата после выполнения func (обязательно,
                                            если задана функция, иначе вернет пустое значение)
depends_on=имя                             ;значение поля заполняется, если не пустое значение поля <имя>

PS. Если в col_config указано несколько номеров колонок, то данные из этих колонок будут разнесены по разным строкам
выходного документа. Приимер см. gisconfig_002_00.ini, раздел [pp_charges_1], [pp_charges_3] и др.
В параметре offset_row_data можно задавать как абсолютное так и отностительное смещение (относительно
текущей строки).
Для задания относительного смещения необходимо перед числовым значением указать знак "+" или "-".
Например, offset_row_data=+1,-1
В параметре func= можно указывать несколько функций для одновременной обработки. Для этого используется знак "+" или "-"(для числовых значений),
например func=column_name+id. В этом случае входные данные будут переданы в обе функции, а результаты функций конкатенируются или суммируется если тип поля float.
В параметре pattern можно указывать ссылку на регулярное выражение, заданное в описании другого поля,
например: pattern=@0 означает, что выражение будет браться из описание этого параметра в разделе [имя_0]
Если после знака @ ничего не указано, то регулярное выражение берется из параметра condition_begin_team


[имя_x_y] ; дополнительная обработка поля (если в основной пустое значение) y-число от [0:]
Параметры те же, что и в [имя_x] кроме name.

Встроенные функции (возвращают строку):
    'period_month': игнорируя входные данные возвращает месяц периода (mm)
    'period_year': игнорируя входные данные возвращает год периода (yyyy)
    'column_name': получает значение из колонки, а возвращает имя этой колонки или имя поля (name)
    'column_value(<номер поля>)': игнорируя входные данные возвращает значение колонки, номер которой указан в скобках
    'hash': получает значение и возвращает хеш по нему
    'uuid': получает значение и возвращает guid по нему
    'id': получает значение и добавляет к нему yyyy_mm из параметра "period"
    'param(<name>)' : значение параметра <name>
    'spacerem' : удаляет все пробелы
    'spacerepl' : заменяет пробелы на подчеркивание
    'round2'    : окуругление числа до 2-х знаков
    'round4'    : окуругление числа до 4-х знаков


PS. period - если не задан, то по умолчанию текущая дата в строковом формате (dd.mm.yyyy)
По остальным, если не заданы, то по умолчанию пустая строка или ноль для числовых данных в строковом формате
В качестве входных данных передаются либо значения полей, указанных в параметре col_config, либо результат обработки от предыдущих функций до запятой. Исключение составляют функции с параметрами, задаными в круглых скобхах (column_value и param) - в эти функции передаются значения, указанные в скобках.

Если перед именем функции стоит префикс "check_", например func=check_column_value(2), то функция (без префикса) выполняется и в случае положительной проверки результата по шаблону (func_pattern) возвращается неизмененное значение
входных данных. Если же результат проверки отрицательный, то возвращается пустая строка.
