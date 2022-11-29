def get_ident(name: str) -> str:
    # name = [item.capitalize() for item in name]
    result = "".join(c for c in name.title() if c.isalnum())
    result = result.replace('Итого','')
    return result

def get_reg(name: str) -> str:
    name = name.replace('\\','\\\\')
    name = name.replace('[','\[').replace(']','\]')
    name = name.replace('(','\(').replace(')','\)')
    name = name.replace('.','[.]')
    return f'^{name.rstrip().replace(";","$;^")}$'


