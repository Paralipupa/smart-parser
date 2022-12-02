def get_ident(name: str) -> str:
    # name = [item.capitalize() for item in name]
    result = "".join(c for c in name.title() if c.isalnum())
    result = result.replace('Итого', '')
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
