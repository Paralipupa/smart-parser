import fileinput


def set_lines() -> list:
    return {'0': [], '1': [], '1a': [], '2': [],
            '2a': [], '3': [], '9': [], 'param': {}, 'dic': {}}


def set_parameters() -> list:
    return ['name',  'border_column_left', 'border_column_right']


def get_ident(name: str) -> str:
    result = "".join(c for c in name.title() if c.isalnum())
    result = result.replace('Итого ', '')
    return result


def get_reg(name: str) -> str:
    name = name.replace('\\', '\\\\').replace('/', '\/')
    name = name.replace('[', '\[').replace(']', '\]')
    name = name.replace('(', '\(').replace(')', '\)')
    name = name.replace('.', '[.]').replace('_', '')
    return f'^{name.rstrip().replace(";","$;^")}$'


def get_name(name: str, names: list) -> str:
    j = 0
    while any([x for x in names if x == (name if j == 0 else f"{name}_{j}")]):
        j += 1
    name = name if j == 0 else f"{name}_{j}"
    names.append(name)
    return name


def get_lines(lines: list) -> list:
    l = []
    if len(lines['1a']) == 0 and len(lines['2a']) == 0:
        ll = lines['1'][-1:]
        l.extend(lines['1'][:-1])
        l.extend(lines['2'])
    else:
        ll = lines['1a'][-1:]
        l.extend(lines['1a'][:-1])
        l.extend(lines['2a'])
    l = sorted(l, key=lambda x: x['name'])
    l.extend(ll)
    return l


def write_config(filenames: list, path: str, output: str = 'gis_config.ini'):
    file_name = f'{path}/ini/{output}'
    with open(file_name, 'w') as fout, fileinput.input(filenames) as fin:
        for line in fin:
            fout.write(line)


def sorted_lines(lines: list) -> list:
    lines['1'] = sorted(lines["1"], key=lambda x: x['name'])
    lines['2'] = sorted(lines["2"], key=lambda x: x['name'])
    lines['3'] = sorted(lines["3"], key=lambda x: x['name'])
    lines['1a'] = sorted(lines["1a"], key=lambda x: x['name'])
    lines['2a'] = sorted(lines["2a"], key=lambda x: x['name'])
    return lines
