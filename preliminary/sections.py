from utils import get_ident, get_name, get_lines, get_func_name
from settings import *


def write_section_caption(**kwargs):
    n = 80
    kwargs.get("file").write("\n")
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
    # kwargs.get("file").write("\n")
    return


def write_section_org_ppa_guid(**kwargs):
    __write_section_head(**kwargs)
    kwargs.get("file").write("pattern=@\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=inn\n")
    # kwargs.get("file").write("\n")
    return


def write_section_contract(**kwargs):
    __write_section_head(**kwargs)
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=_+К,spacerepl,hash\n")
    return


def __write_section_service_internal_id(**kwargs):
    service_names: list = get_lines(kwargs.get("lines"))
    kwargs["line"] = dict(index=0, line=get_lines(kwargs.get("lines"))[0])
    if not kwargs.get("lines")["dic"].get("service") or len(service_names) > 2:
        __write_sec_main(**kwargs)
        __write_sec_offset_row_col(**kwargs)
        __write_sec_offset_pattern(**kwargs)
        __write_sec_func(**kwargs)
        __write_sec_sub_fields(**kwargs)
        __write_service_fields(**kwargs)

    else:
        kwargs.get("file").write("pattern=@Прочие\n")
        kwargs.get("file").write("row_data=0\n")
        if kwargs.get("lines")["dic"].get("service"):
            col = kwargs.get("lines")["dic"]["service"][0]["col"]
            kwargs.get("file").write(f"col_config={col}\n")
            if kwargs.get("sec_is_hash"):
                kwargs.get("file").write(f"func=hash\n")
    # kwargs.get("file").write("\n")
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
    # kwargs.get("file").write("\n")
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
    # kwargs.get("file").write("\n")
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
    # kwargs.get("file").write("\n")
    return


def write_section_service_internal_id(**kwargs):
    __write_section_head(**kwargs)
    __write_section_service_internal_id(**kwargs)
    return


def write_section_rr(**kwargs):
    service_names = get_lines(kwargs.get("lines"))
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
            name = get_name(get_ident(service_names[0]["name"].split(";")[0]))
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
            for i, line in enumerate(service_names[1:]):
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
    # kwargs.get("file").write("\n")
    return


def write_section(**kwargs):
    __write_section_head(**kwargs)
    kwargs["line"] = dict(index=0, line=get_lines(kwargs.get("lines"))[0])
    kwargs["sec_prefix"] = __get_sec_prefix(**kwargs)
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix')}"
    )
    if (
        fld_param
        or kwargs.get("sec_func")
        or kwargs.get("sec_is_ident")
        or kwargs.get("sec_is_func_name")
        or "internal_id" in kwargs.get("sec_name")
    ):
        __write_sec_main(**kwargs)
        __write_sec_offset_row_col(**kwargs)
        __write_sec_offset_pattern(**kwargs)
        __write_sec_type(**kwargs)
        __write_sec_func(**kwargs)
        __write_sec_sub_fields(**kwargs)
    __write_service_fields(**kwargs)


def __write_section_head(**kwargs):
    kwargs.get("file").write(
        f"\n[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}]\n"
    )
    kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
    kwargs.get("file").write(f"name={kwargs.get('sec_name')}\n")
    return


def __write_section_internal_id(**kwargs):
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")
    kwargs.get("file").write("row_data=0\n")
    kwargs.get("file").write("func=spacerepl,hash\n")


# ----------------------------------------------------------------------------------------------------------
def __get_sec_prefix(**kwargs):
    if kwargs.get("sec_prefix") is None:
        kwargs["sec_prefix"] = f"_{kwargs.get('sec_type')}"
    if (
        kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )
        is None
    ):
        kwargs["sec_prefix"] = ""
    return kwargs["sec_prefix"]


def __get_is_service_sub_flds(**kwargs) -> bool:
    service_names: list = get_lines(kwargs.get("lines"))
    return (
        (kwargs.get("sec_is_service") is None or bool(kwargs.get("sec_is_service")))
        and len(service_names) > 1
    ) and (
        (kwargs.get("sec_is_ident") or kwargs.get("sec_is_func_name"))
        or (
            bool(
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
    )


def __write_sec_main(**kwargs):
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")


def __write_sec_offset_row_col(**kwargs):
    if __get_is_service_sub_flds(**kwargs) and kwargs.get("lines")["dic"].get(
        "service"
    ):
        kwargs.get("file").write(
            f'offset_col_config={kwargs.get("lines")["dic"]["service"][0]["col"]}\n'
        )
    else:
        if not kwargs.get("lines")["dic"].get("service"):
            kwargs.get("file").write("row_data=0\n")
        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ):
            col = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["col"]
            kwargs.get("file").write(f"offset_col_config={col}\n")


def __write_sec_offset_pattern(**kwargs):
    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )[0]["pattern"]:
            pattern = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["pattern"].strip()
            kwargs.get("file").write(f"offset_pattern={pattern}\n")
        else:
            if __get_is_service_sub_flds(**kwargs):
                if (
                    kwargs.get("lines")["dic"].get("service")
                    or kwargs.get("sec_is_ident")
                    or kwargs.get("sec_is_func_name")
                ):
                    service_names: list = get_lines(kwargs.get("lines"))
                    name = get_name(get_ident(service_names[0]["name"].split(";")[0]))
                    kwargs.get("file").write(f"offset_pattern=@{name}\n")
                else:
                    kwargs.get("file").write("offset_pattern=.+\n")
            else:
                kwargs.get("file").write("offset_pattern=.+\n")
    else:
        if __get_is_service_sub_flds(**kwargs) and kwargs.get("lines")["dic"].get("service"):
            service_names: list = get_lines(kwargs.get("lines"))
            name = get_name(get_ident(service_names[0]["name"].split(";")[0]))
            kwargs.get("file").write(f"offset_pattern=@{name}\n")


def __write_sec_type(**kwargs):
    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
        if kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )[0]["type"]:
            oft = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["type"][0]
            kwargs.get("file").write(f"offset_type={oft}\n")


def __write_sec_func(**kwargs):
    service_field = kwargs.get("line")
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    suffix = f'+{kwargs.get("sec_suffix")}' if kwargs.get("sec_suffix") else ""
    hash = ",hash" if kwargs.get("sec_is_hash") else ""
    if fld_param and fld_param[0]["func"] and service_field["index"] == 0:
        func = kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["func"][0]
        kwargs.get("file").write(f"func={func}\n")
    elif kwargs.get("sec_func") and service_field["index"] == 0:
        if kwargs.get("sec_func")[0] != "!":
            kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
        else:
            kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
            kwargs.get("file").write(f"func_is_no_return=true\n")
    elif kwargs.get("sec_is_ident"):
        if fld_param:
            ident = get_ident(fld_param[0]["name"])
        else:
            ident = get_func_name(service_field["line"]["name"].split(";")[0])
        kwargs.get("file").write(f"func=id+{ident}{suffix},spacerepl{hash}\n")
    elif kwargs.get("sec_is_func_name"):
        if fld_param and not __get_is_service_sub_flds(**kwargs):
            ident = get_ident(fld_param[0]["name"])
        else:
            ident = get_func_name(service_field["line"]["name"].split(";")[0])
        kwargs.get("file").write(f"func={ident}{hash}\n")
    elif __get_is_service_sub_flds(**kwargs) and kwargs.get("lines")["dic"].get(
        "service"
    ):
        col_fld = kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["col"]
        col_service = kwargs.get("lines")["dic"]["service"][0]["col"]
        if col_fld != col_service:
            kwargs.get("file").write(f"func=column_value({col_fld})\n")
            kwargs.get("file").write(f"func_is_empty=true\n")


def __write_sec_sub_fields(**kwargs):
    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
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


def __write_service_fields(**kwargs):
    if __get_is_service_sub_flds(**kwargs):
        service_names: list = get_lines(kwargs.get("lines"))
        for i, line in enumerate(service_names[1:]):
            if (
                kwargs.get("lines")["dic"].get("service")
                or kwargs.get("sec_is_ident")
                or kwargs.get("sec_is_func_name")
            ):
                kwargs["line"] = dict(index=i, line=line)
                kwargs.get("file").write(
                    f"\n[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
                )
                kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")
                if kwargs.get("lines")["dic"].get("service"):
                    name = get_name(get_ident(line["name"].split(";")[0]))
                    kwargs.get("file").write(f"offset_pattern=@{name}\n")
                if kwargs.get("sec_is_ident"):
                    if kwargs.get("sec_suffix"):
                        kwargs.get("file").write(
                            f'func=id+{get_func_name(line["name"].split(";")[0])}+{kwargs.get("sec_suffix")},spacerepl{",hash" if kwargs.get("sec_is_hash") else ""}\n'
                        )
                    else:
                        kwargs.get("file").write(
                            f'func={get_func_name(line["name"].split(";")[0])}{",hash" if kwargs.get("sec_is_hash") else ""}\n'
                        )
                else:
                    if kwargs.get("sec_is_func_name"):
                        kwargs.get("file").write(
                            f'func={get_func_name(line["name"].split(";")[0])}{",hash" if kwargs.get("sec_is_hash") else ""}\n'
                        )
