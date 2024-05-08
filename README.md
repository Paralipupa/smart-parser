## Парсинг файла MS Excel

Данные распознаются на основании конфигурацонного файла вида <b>gisconfig_###_##[наименование].ini</b> и записывааются в файлы csv<br/>

## Разделы конфигурационного файла ini:

<b>[check]</b><br/>

Раздел используется для проверки совместимости исходного файла MS Excel и конфигурацонного файла.</br>

Параметры:<br/>
<ul>
<li><b>row</b>=[диапазон чисел] - строки листа файла для проверки значения<br/>
<li><b>column</b>=[диапазон чисел] - колонки листа файла для проверки значения<br/>
<li><b>pattern</b>=[регулярное выражение] - условие совместимости данной конфигурации и данных листа MS Excel<br/>
<li><b>func</b>=[имя функции] - применить функцию после нахождения значения по шаблону<br/>
<li><b>func_pattern</b>=[рег.выражения] - проверить соответствие шаблону после применения функции<br/>
</ul>

P.S. (здесь и далее)<br/> 
<b>[диапазон чисел]</b> -  задается либо числом, либо перечислением числовых значений через запятую, например: 0,1,3,5; либо через указание интервала с использованием знака "<", например: 0<4 что соответсвует 0,1,2,3,4 <br/>
<b>pattern</b> - регулярное выражение, может быть составным в виде дополнительных  строк, вида <b>patern_N=</b> - где N - порядковый номер, начиная от нуля<br/>

Нумерация колонок и строк начинается с нуля.<br/>
В качестве исходного файла рассматривается файл MS Excel.<br/>

##

<b>[header]</b><br/>

Раздел используется, если в файле более одной таблицы. Например "квитанции за декабрь 2021.xml"<br/>

Параметры:<br/>
<ul>
<li><b>row</b>=[диапазон чисел] - строки листа MS Excel для проверки заголовочной области<br/>
<li><b>column</b>=[диапазон чисел] - колонки листа MS Excel для проверки заголовочной области<br/>
<li><b>pattern</b>=[регулярное выражение] - поиск начала заголовочной области на листе MS Excel<br/>
<li><b>offset_pattern</b>=[рег. выражение] - шаблон "якоря" (дополнительное уточнение) данного параметра<br/>
<li><b>offset_row</b>=[диапазон чисел] -номера строк поиска "якоря" для данного параметра<br/>
<li><b>offset_col</b>=[диапазон чисел] - номера столбцов поиска "якоря" данного параметра<br/>
<li><b>func</b>=[имя функции] - значение, результат выполнения функции<br/>
</ul>

##
<b>[main]</b><br/>

Параметры:<br/>
<ul>
<li><b>path_output</b>=[строка] - путь выходного файла (по-умолчанию output в текущем каталоге)<br/>
<li><b>row_start</b>=[число] - начальная строка обработки. По-умолчанию, 0<br/>
<li><b>page_names</b>=[имя листа] - имена листов, разделенные знаком <b>"|", в файле MS Excel определяющие порядок обработки</b><br/>
<li><b>page_index</b>=[номер листа] - номер или номера листов в файле. Если указано значение <b>-1</b>, то просматриваются все имеющиеся листы файла<br/>
<li><b>max_columns</b>=[число] - количество просматриваемых колонок для поиска заголовков таблицы<br/>
<li><b>max_rows_heading</b>=[число] - количество просматриваемых строк для поиска заголовков таблицы<br/>
<li><b>rows_exclude</b>=[диапазон чисел] - не обрабатываемые порядковые номера строк в табличной области<br/>
<li><b>border_column_left=[число]</b> - левая граница колонок с услугами<br/>
<li><b>border_column_right=[число]</b> - правая граница колонок с услугами<br/>
<li><b>checking_rows=[наименование колонки]::[шаблон]</b> - условие валидности строк исходной таблицы<br/>

</ul><br/>

##
<b>[pattern]</b>, <b>[pattern_0]...<b>[pattern_N]</b></b><br/>

Разделы шаблонов регулярных выражений можно использовать в виде сылок (@name) в других разделах<br/>

Параметры:<br/>
<ul>
<li><b>name</b>=[строка] - произвольное имя шаблона<br/>
<li><b>pattern</b>=[рег.выражение] - регулярное выражение<br/>
</ul>

##
<b>[headers_0]</b>, <b>[headers_1]</b>...<b>[headers_N]</b><br/>
 
Разделы для нахождения значений перед таблицей.  <br/>
Эти значения используются как значения переменных, к которым можно ссылаться в дальнейшем.</br>

Параметры:<br/>
<ul>
<li><b>name</b>=[строка] - имя параметра, например - name=period<br/>
<li><b>row</b>=[диапазон чисел] -номера строк листа, для поиска значения параметра<br/>
<li><b>column</b>=[диапазон чисел] - номера колонк листа, для поиска значения параметра<br/>
<li><b>pattern</b>=[рег.выражение] - шаблон для поиска значения параметра. В качестве значения можно указывать ссылку (@name) на ранее определенный шаблон в разделах [pattern_N]<br/>
<li><b>value</b>=[строка] - значение, которое берется при срабатывании шаблона. <br/>
При отсутствии данного параметра берется значение из найденной ячейки листа. <br/>
<li><b>func</b>=[имя функции] - в качестве исходного значения берется не значение из ячейки, а результат выполнения функции над этим значением.<br/>
</ul><br/>

##
<b>[footers_0]</b>, <b>[footers_1]</b>...<b>[footers_N]</b><br/>

Разделы для нахождения значений после таблицы, если  на листе размещено более одной таблицы  (редкий случай)<br/>
Параметры как у [headers_N]</br>

##
<b>[col_0]</b>, <b>[col_1]</b>...<b>[footers_N]</b><br/>

Разделы для определения колонок таблицы<br/>

<ul>
<li><b>name</b>=[строка] - идентификатор колонки<br/>
<li><b>alias</b>=[строка] - наименование колонки. При отсутствии принимает значение из параметра <b>name</b> <br/>
<li><b>pattern</b>=[рег. выражение] - шаблон заголовка колонки таблицы<br/>
<li><b>condition_begin_team</b>=[рег. выражение] - шаблон начала группы данных соответствующих идентификатору группы. Для формирования группы записей исходной таблицы, соответствующих одному идентификатору  (обычно лицевому счету).<br/>
<li><b>condition_end_table</b>=[рег. выражение] - шаблон окончания табличных данных. Условие когда таблица заканчивается. Используется когда есть несколько таблиц на одном листе, идущих друг за другом (редкий случай).<br/>
<li><b>col_data_offset</b>=[диапазон чисел] - номера колонок листа откуда будут считываться данные. Т.е. шаблон соответствует данным из одной колонки, а фактически данные могут браться из другой.<br/>
<li><b>offset_pattern</b>=[рег. выражение] - шаблон "якоря" (дополнительное уточнение) для заголовка колонки. Если есть несколько одинаковых названий колонок, то нужен ориентир из данных в рядом стоящих ячейках. <br/>
<li><b>offset_row</b>=[диапазон чисел] -номера строк поиска "якоря" для заголовка данной колонки<br/>
<li><b>offset_col</b>=[диапазон чисел] - номера столбцов поиска "якоря" для заголовка данной колонки<br/>
<li><b>border_column_left</b>=[число] - порядковый номер колонки в конфигурации (col_N) ограничивающий слева список колонок относящихся к услугам<br/>
<li><b>border_column_right</b>=[число] -порядковый номер колонки в конфигурации ограничивающий справа список колонок относящихся к услугам<br/>
<li><b>is_optional</b>=[<i>false</i>|true] - признак необязательной колонки в таблице. По-умолчанию присутствие колонки обязательно (false)<br/>
<li><b>is_duplicate</b>=[<i>false</i>|true] - признак того, что данные из колонки исходной таблицы могут содержаться в других колонках конфигурации. По-умолчанию, не повторяются (false)<br/>
<li><b>is_unique</b>=[<i>false</i>|true] - признак того, что в исходной таблице берется только одно значение (остальные колонки таблицы, найденные по шаблону игнорируются)<br/>
<li><b>is_only_after_stable</b>=[<i>false</i>|true] - колонка ищется только после нахождения всех обязательных (optional=false) колонок (если параметр задан, то для нее параметр <br/><i>is_optional</i> всегда 'true'). Используется для поиска колонок в исходной таблице с наименованиями различных услуг.<br/>
</ul><br/>

P.S.<br/>

Если под условие заданное в <b>pattern</b> попадает несколько колонок таблицы (за исключением, когда is_unique=true), то данные по ним суммируются при числовых или конкатенируются при строковых значениях.<br/>. Например, для начисленные суммы+пени+перерасчет.<br/>

<b>condition_begin_team</b> и <b>condition_end_table</b> задаются в любой из колонок, где необходимо проверить условия. При этом в случае совпадения по шаблону  в нескольких колонках, за основу берется колонка с наименьшим номером, остальные игнорируются.<br/>

##
<b>[doc_0]</b>, <b>[doc_1]</b>...<b>[doc_N]</b><br/>

Разделы для настройки выходного документа (файла csv)<br/>
<ui>
<li><b>name</b>=[строка] - наименование выходного документа. Например, name=accounts<br/>
<li><b>rows_exclude</b>=[диапазон чисел] - не обрабатываемые порядковые номера строк в группе.<br/>
<li><b>required_fields</b>=[имена полей] - список обязательных для заполнения полей.<br/>
Например: required_fields=r1,r2,r3. Обязательным является заполение
хотя бы одного поля из списка. Если список не задан, то выходная запись формируется в случае заполнения любого из полей документа.<br/>
<li><b>func_after</b>=[имя функции] - запускается после обработки документа<br/>
<li><b>type</b>=[тип] - тип документа. Например, если dictionary, то данные заносятся в глобальный  словарь. <br/>
</ui><br/>

##
<b>[имя_0]</b>,<b>[имя_1]</b>,...,<b>[имя_N]</b><br/>
<b>имя</b> соответствует значению из параметра <b>name</b> раздела [doc_N]. <br/>

Разделы описания полей выходного документа (файла csv)<br/>

Параметры:<br/>
<ul>
<li><b>name</b>=[строка] -  имя поля в документе<br/>
<li><b>pattern</b>=[рег.выражение] - шаблон для проверки значения данного поля<br/>
<li><b>rows_exclude</b>=[диапазон чисел] - не обрабатываемые номера строк из группы <br/>
<li><b>col_config</b>=[диапазон чисел] - номер(а) колонок (из раздела [col_N]) для поиска по заданному шаблону<br/>
<li><b>row_data</b>=[диапазон чисел] - номер(а) строк в группе. Если параметр не задан, то берутся все строки<br/>
<li><b>type</b>=[int|float] - числовой тип данных текущего поля. По-умолчанию - строковые значения<br/>
<li><b>offset_col_config</b>=[диапазон чисел] - номер колонки (из раздела [col_N]) берутся значения по найденному шаблону. Если не  заданно, то данные берутся из колонки, указаной в col_config<br/>
<li><b>offset_row_data</b>=[диапазон чисел] -порядковый номера строки в группе откуда берутся значения по найденному шаблону<br/>
<li><b>offset_pattern</b>=[рег.выражение] - шаблон для данных из колонки offset_col и offset_row_data<br/>
<li><b>offset_type</b>=[тип] - тип значения<br/>
<li><b>func</b>=[имя фунции или параметра] - имена встроенных функций или заданых параметров из раздела <b>headers</b> для обработки полученного
значения поля, например: func=id,uuid. При этом обработка данных происходит последовательно с передачей полученного значений в следующую функцию, указанную после запятой.<br/>
<li><b>func_pattern</b>=[рег.выражение] - для проверки результата после выполнения func (обязательно, если задана функция, иначе вернет пустое значение)<br/>
<li><b>func_is_no_return</b>=[имя функции] - признак того, что функция не возвращает значения. Просто отрабатывает.<br/>
<li><b>func_is_empty</b>=[true|false] = Применять или нет функцию, если исходнное значение, взятое из ячейки таблицы пусто.<br/>
<li><b>depends_on</b>=[имя] - значение поля заполняется, если не пустое значение поля, заданное параметром name=имя. Например, дату не заполнять если нет начислений.<br/>
</ul><br/>

P.S.<br/>

Если в <b>col_config</b> указано несколько номеров колонок, то данные из этих колонок будут разнесены по разным строкам выходного документа.<br/>

В параметре <b>offset_row_data</b> можно задавать как абсолютное так и отностительное смещение (относительно текущей строки).<br/>
Для задания относительного смещения необходимо перед числовым значением указать знак "+" или "-".<br/>
Например, offset_row_data=+1,-1<br/>

В параметре <b>func=</b> можно указывать несколько функций для одновременной обработки. Для этого используется знак "+" или "-"(для числовых значений).<br/>
Например func=column_name+id.<br/> 
В этом случае входные данные будут переданы в обе функции, а результаты функций конкатенируются или суммируется если тип поля float.<br/>

В параметре <b>pattern</b> можно указывать ссылку на регулярное выражение, заданное в описании другого поля.<br/>
Например: pattern=@0 означает, что выражение будет браться из описание этого параметра в разделе <b>[имя_0]</b><br/>
Если после знака @ ничего не указано, то регулярное выражение берется из параметра <b>condition_begin_team</b></br>


##
[имя_N_M] ; дополнительная обработка поля (если в основной пустое значение) M-число от [0:]<br/>

Параметры те же, что и в [имя_N] кроме name.<br/>

Встроенные функции (возвращают строку):</br>
<ul>
<li>inn - ИНН<br/>
<li>period_first - первый день месяца<br/>
<li>period_last - последний день месяца<br/>
<li>period_month - игнорируя входные данные возвращает месяц периода (mm)<br/>
<li>period_year - игнорируя входные данные возвращает год периода (yyyy)<br/>
<li>column_name(число) - имя колонки<br/>
<li>account_number - р.с банка<br/>
 <li>bik - бик банка<br/>
 <li>column_value -  игнорируя входные данные возвращает значение колонки, номер которой указан в скобках<br/>
 <li>hash - получает значение и возвращает хеш по нему<br/>
 <li>guid - получает значение и возвращает guid по нему<br/>
 <li>param(name) - значение параметра <b>name</b><br/>
 <li>spacerem - удаляет все пробелы<br/>
 <li>spacerepl - заменяет пробелы на подчеркивание<br/>
<li>round2 - окуругление числа до 2-х знаков<br/>
<li>round4 - окуругление числа до 4-х знаков<br/>
<li>round6 - окуругление числа до 6-х знаков<br/>
<li>opposite - возвращает число  с противоположным знаком<br/>
<li>dictionary - значение словаря<br/>
<li>to_date - дата<br/>
 <li>id - идентификатор, текущее значение_mmYYYY<br/>
 <li>account_type - <br/>
 <li>fillzero9 -  <br/>
 <li>check_bank_accounts - проверка банка<br/>
</ul><br/>

P.S.<br/> 
<b>period</b> - если не задан, то по умолчанию текущая дата в строковом формате (dd.mm.yyyy)<br/>

По остальным, если не заданы, то по умолчанию пустая строка или ноль для числовых данных в строковом формате</br>

В качестве входных данных передаются либо значения полей, указанных в параметре <b>col_config</b>, либо результат обработки от предыдущих функций до запятой. <br/>
Исключение составляют функции с параметрами, задаными в круглых скобхах (<b>column_value</b>) - в эти функции передаются значения, указанные в скобках.</br>

Если перед именем функции стоит префикс "check_", например func=check_column_value(2), то функция (с наименование после префикса "check_") выполняется и в случае положительной проверки результата по шаблону (func_pattern) возвращается неизмененное значение входных данных. Если же результат проверки отрицательный, то возвращается пустая строка.<br/>


