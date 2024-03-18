from utils import get_ident, get_name, get_lines, get_func_name
from settings import *


def write_section_caption(**kwargs):
    n = 80
    kwargs.get("file").write(";" + "".rjust(n, "#") + "\n")
    kwargs.get("file").write(
        ";"
        + str(
            f" {kwargs.get('sec_type')} ".rjust(
                (n - len(kwargs.get("sec_type")) - 2) // 2, "-"
            )
        ).ljust(n, "-")
        + "\n"
    )
    kwargs.get("file").write(";" + "".rjust(n, "#") + "\n")
    kwargs.get("file").write("\n")
    return


def write_section_doc(**kwargs):
    kwargs.get("file").write(f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}]\n")
    kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
    kwargs.get("file").write(f"name={kwargs.get('sec_name')}\n")
    if kwargs.get("required_fields"):
        kwargs.get("file").write(f"required_fields={kwargs.get('required_fields')}\n")
    kwargs.get("file").write("\n")
    return


def write_section_org_ppa_guid(**kwargs):
    __write_section_head(**kwargs)
    kwargs.get("file").write("pattern=@\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=inn\n")
    kwargs.get("file").write("\n")
    return


def write_section_contract(**kwargs):
    __write_section_head(**kwargs)
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=_+К,spacerepl,hash\n\n")
    kwargs.get("file").write("\n")
    return


def __write_section_service_internal_id(**kwargs):
    l: list = get_lines(kwargs.get("lines"))
    if not kwargs.get("lines")["dic"].get("service") or len(l) > 2:
        kwargs.get("file").write("pattern=@0\n")
        kwargs.get("file").write("col_config=0\n")
        if kwargs.get("lines")["dic"].get("service"):
            kwargs.get("file").write(
                f'offset_col_config={kwargs.get("lines")["dic"]["service"][0]["col"]}\n'
            )
            name = get_name(get_ident(l[0]["name"].split(";")[0]))
            kwargs.get("file").write(f"offset_pattern=@{name}\n")
            # kwargs.get("file").write(f"func_is_empty=true\n")
        else:
            kwargs.get("file").write("row_data=0\n")
        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}_{kwargs.get('sec_type')}"
        ):
            if kwargs.get("is_ident"):
                ident = get_ident(
                    kwargs.get("lines")["dic"][
                        f"{kwargs.get('sec_name')}_{kwargs.get('sec_type')}"
                    ][0]["name"]
                )
                if kwargs.get("sec_suffix"):
                    kwargs.get("file").write(
                        f"func=id+{ident}+{kwargs.get('sec_suffix')},spacerepl,hash\n"
                    )
                else:
                    ident = get_ident(
                        kwargs.get("lines")["dic"][
                            f"{kwargs.get('sec_name')}_{kwargs.get('sec_type')}"
                        ][0]["name"]
                    )
                    hash = ",hash" if kwargs.get("sec_is_hash") else ""
                    kwargs.get("file").write(f"func={ident}{hash}\n")
            else:
                ident = get_ident(
                    kwargs.get("lines")["dic"][
                        f"{kwargs.get('sec_name')}_{kwargs.get('sec_type')}"
                    ][0]["name"]
                )
                kwargs.get("file").write(f"func={ident},hash\n")
        else:
            if kwargs.get("is_ident"):
                if kwargs.get("sec_suffix"):
                    kwargs.get("file").write(
                        f'func=id+{get_func_name(l[0]["name"].split(";")[0])}+{kwargs.get("sec_suffix")},spacerepl,hash\n'
                    )
                else:
                    kwargs.get("file").write(
                        f'func={get_func_name(l[0]["name"].split(";")[0])}{",hash" if kwargs.get("sec_is_hash") else ""}\n'
                    )
            else:
                kwargs.get("file").write(
                    f'func={get_func_name(l[0]["name"].split(";")[0])},hash\n'
                )
        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}_{kwargs.get('sec_type')}"
        ):
            for i, line in enumerate(
                kwargs.get("lines")["dic"][
                    f"{kwargs.get('sec_name')}_{kwargs.get('sec_type')}"
                ][1:]
            ):
                kwargs.get("file").write(
                    f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
                )
                kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
                if kwargs.get("is_ident"):
                    if kwargs.get("sec_suffix"):
                        kwargs.get("file").write(
                            f'func=id+{get_ident(line["name"])}+{kwargs.get("sec_suffix")},spacerepl,hash\n'
                        )
                    else:
                        kwargs.get("file").write(
                            f'func={get_ident(line["name"])}{",hash" if kwargs.get("sec_is_hash") else ""}\n'
                        )
                else:
                    kwargs.get("file").write(f'func={get_ident(line["name"])},hash\n')
        else:
            kwargs.get("file").write("\n")
            kwargs["l"] = l
            __write_sub_fields(**kwargs)
    else:
        kwargs.get("file").write("pattern=@Прочие\n")
        kwargs.get("file").write("row_data=0\n")
        if kwargs.get("lines")["dic"].get("service"):
            col = kwargs.get("lines")["dic"]["service"][0]["col"]
            kwargs.get("file").write(f"col_config={col}\n")
            if kwargs.get("sec_is_hash"):
                kwargs.get("file").write(f"func=hash\n")
    kwargs.get("file").write("\n")
    return


def write_section_internal_id(**kwargs):
    __write_section_head(**kwargs)
    if kwargs.get("sec_is_service"):
        __write_section_service_internal_id(**kwargs)
    else:
        __write_section_internal_id(**kwargs)
    return


def write_section_fias(**kwargs):
    __write_section_head(**kwargs)
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=fias\n")
    kwargs.get("file").write("func_is_no_return=true\n")
    kwargs.get("file").write("\n")
    return


def write_section_address(**kwargs):
    __write_section_head(**kwargs)
    if kwargs.get("lines")["dic"].get(f"{kwargs.get('sec_name')}"):
        kwargs.get("file").write("pattern=.+\n")
        col = kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["col"]
        kwargs.get("file").write(f"col_config={col}\n")
        kwargs.get("file").write("row_data=0\n")
        if (
            kwargs.get("lines")["dic"].get(f"{kwargs.get('sec_name')}")
            and kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["func"]
        ):
            func = kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["func"][0]
            kwargs.get("file").write(f"func={func}\n")
        elif kwargs.get("lines")["dic"].get("room_number"):
            kwargs.get("file").write(
                f'func=_+кв.+column_value({kwargs.get("lines")["dic"]["room_number"][0]["col"]})\n'
            )
    else:
        kwargs.get("file").write(f"col_config=0\n")
        kwargs.get("file").write("row_data=0\n")
        kwargs.get("file").write("pattern=@0\n")
        if (
            kwargs.get("lines")["dic"].get(f"{kwargs.get('sec_name')}")
            and kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["func"]
        ):
            func = kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["func"][0]
            kwargs.get("file").write(f"func={func}\n")
        elif kwargs.get("lines")["dic"].get("room_number"):
            kwargs.get("file").write(
                f'func=address+кв.+column_value({kwargs.get("lines")["dic"]["room_number"][0]["col"]})\n'
            )
        else:
            kwargs.get("file").write(f"func=address\n")
        kwargs.get("file").write("func_is_no_return=true\n")
    kwargs.get("file").write("\n")
    return


def write_section_account_internal_id(**kwargs):
    __write_section_head(**kwargs)
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    if kwargs.get("lines")["dic"].get(f"{kwargs.get('sec_name')}"):
        col = kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["col"]
        kwargs.get("file").write(f"offset_col_config={col}\n")
        kwargs.get("file").write("offset_pattern=.+\n")
    if (
        kwargs.get("lines")["dic"].get(f"{kwargs.get('sec_name')}")
        and kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["func"]
    ):
        func = kwargs.get("lines")["dic"][f"{kwargs.get('sec_name')}"][0]["func"][0]
        kwargs.get("file").write(f"func={func}\n")
    else:
        kwargs.get("file").write("func=spacerepl,hash\n")
    kwargs.get("file").write("\n")
    return


def write_section_service_internal_id(**kwargs):
    __write_section_head(**kwargs)
    kwargs["sec_is_ident"] = False
    __write_section_service_internal_id(**kwargs)
    return


def write_section_rr(**kwargs):
    l = get_lines(kwargs.get("lines"))
    __write_section_head(**kwargs)
    if kwargs.get("sec_prefix") is None:
        kwargs["sec_prefix"] = f"_{kwargs.get('sec_type')}"
    if (
        kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )
        is None
    ):
        kwargs["sec_prefix"] = ""
    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
        if kwargs.get("lines")["dic"].get("service"):
            name = get_name(get_ident(l[0]["name"].split(";")[0]))
            kwargs.get("file").write(f"pattern=@{name}\n")
            kwargs.get("file").write(
                f'col_config={kwargs.get("lines")["dic"]["service"][0]["col"]}\n'
            )
            col = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["col"]
            kwargs.get("file").write(f"offset_col_config={col}\n")
            kwargs.get("file").write("offset_pattern=.+\n")
            kwargs.get("file").write("offset_type=float\n")
            kwargs.get("file").write("func=round6\n")
            for i, line in enumerate(l[1:]):
                kwargs.get("file").write(
                    f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
                )
                kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
                kwargs.get("file").write(f'; {line["name"].rstrip()}\n')
                name = get_name(get_ident(line["name"].split(";")[0]))
                kwargs.get("file").write(f"pattern=@{name}\n")
        else:
            kwargs.get("file").write("pattern=@0\n")
            kwargs.get("file").write("col_config=0\n")
            col = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["col"]
            kwargs.get("file").write(f"offset_col_config={col}\n")
            kwargs.get("file").write("offset_pattern=.+\n")
            kwargs.get("file").write("offset_type=float\n")
            kwargs.get("file").write("func=round6\n")
            for i, line in enumerate(
                kwargs.get("lines")["dic"][
                    f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
                ][1:]
            ):
                kwargs.get("file").write(
                    f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
                )
                kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
                kwargs.get("file").write(f'offset_col_config={line["col"]}\n')
    kwargs.get("file").write("\n")
    return


def write_section(**kwargs):
    __write_section_head(**kwargs)
    l: list = get_lines(kwargs.get("lines"))
    if kwargs.get("sec_prefix") is None:
        kwargs["sec_prefix"] = f"_{kwargs.get('sec_type')}"
    if (
        kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )
        is None
    ):
        kwargs["sec_prefix"] = ""
    is_sub_fld = (
        (kwargs.get("sec_is_service") is None or bool(kwargs.get("sec_is_service")))
        and kwargs.get("lines")["dic"].get("service")
        and bool(
            kwargs.get("lines")["dic"].get(
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            )
        )
        and (
            len(
                kwargs.get("lines")["dic"][
                    f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
                ]
            )
            == 1
        )
    )
    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
        kwargs.get("file").write("pattern=@0\n")
        kwargs.get("file").write("col_config=0\n")

        if kwargs.get("lines")["dic"].get("service") is None:
            kwargs.get("file").write("row_data=0\n")
            col = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["col"]
            kwargs.get("file").write(f"offset_col_config={col}\n")
        else:
            if is_sub_fld:
                kwargs.get("file").write(
                    f'offset_col_config={kwargs.get("lines")["dic"]["service"][0]["col"]}\n'
                )
            else:
                col = kwargs.get("lines")["dic"][
                    f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
                ][0]["col"]
                kwargs.get("file").write(f"offset_col_config={col}\n")

        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )[0]["pattern"]:
            pattern = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["pattern"]
            kwargs.get("file").write(f"offset_pattern={pattern}\n")
        else:
            if is_sub_fld:
                name = get_name(get_ident(l[0]["name"].split(";")[0]))
                kwargs.get("file").write(f"offset_pattern=@{name}\n")
                if not kwargs.get("sec_func"):
                    col = kwargs.get("lines")["dic"][
                        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
                    ][0]["col"]
                    kwargs.get("file").write(f"func=column_value({col})\n")
                    kwargs.get("file").write(f"func_is_empty=true\n")
            else:
                kwargs.get("file").write("offset_pattern=.+\n")

        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )[0]["type"]:
            oft = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["type"][0]
            kwargs.get("file").write(f"offset_type={oft}\n")
        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )[0]["func"]:
            func = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["func"][0]
            kwargs.get("file").write(f"func={func}\n")
        elif kwargs.get("sec_func"):
            if kwargs.get("sec_func")[0] != "!":
                kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
            else:
                kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
                kwargs.get("file").write(f"func_is_no_return=true\n")
        for i, line in enumerate(
            kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][1:]
        ):
            kwargs.get("file").write(
                f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
            )
            kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
            kwargs.get("file").write(f'offset_col_config={line["col"]}\n')
            if line["func"]:
                kwargs.get("file").write(f'func={line["func"][0]}\n')
            elif kwargs.get("sec_func"):
                if kwargs.get("sec_func")[0] != "!":
                    kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
                else:
                    kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
                    kwargs.get("file").write(f"func_is_no_return=true\n")
    elif kwargs.get("sec_func"):
        kwargs.get("file").write("pattern=@0\n")
        kwargs.get("file").write("col_config=0\n")
        kwargs.get("file").write("row_data=0\n")
        if kwargs.get("sec_func")[0] != "!":
            kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
        else:
            kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
            kwargs.get("file").write(f"func_is_no_return=true\n")
    kwargs.get("file").write("\n")

    if is_sub_fld:
        kwargs["l"] = l
        __write_sub_fields(**kwargs)


def __write_section_head(**kwargs):
    kwargs.get("file").write(f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}]\n")
    kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
    kwargs.get("file").write(f"name={kwargs.get('sec_name')}\n")
    return


def __write_section_internal_id(**kwargs):
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=spacerepl,hash\n\n")


def __write_sub_fields(**kwargs):
    for i, line in enumerate(kwargs.get("l")[1:]):
        kwargs.get("file").write(
            f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
        )
        kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
        if kwargs.get("lines")["dic"].get("service"):
            name = get_name(get_ident(line["name"].split(";")[0]))
            kwargs.get("file").write(f"offset_pattern=@{name}\n")
        if kwargs.get("is_ident"):
            if kwargs.get("sec_suffix"):
                kwargs.get("file").write(
                    f'func=id+{get_func_name(line["name"].split(";")[0])}+{kwargs.get("sec_suffix")},spacerepl,hash\n'
                )
            else:
                kwargs.get("file").write(
                    f'func={get_func_name(line["name"].split(";")[0])}{",hash" if kwargs.get("sec_is_hash") else ""}\n'
                )
        else:
            if kwargs.get("is_func"):
                kwargs.get("file").write(
                    f'func={get_func_name(line["name"].split(";")[0])},hash\n'
                )
