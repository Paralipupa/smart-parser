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
        if __is_service_parameters(**kwargs):
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


def __write_section_service_internal_id(**kwargs):
    service_names: list = get_lines(kwargs.get("lines"))
    kwargs["line"] = dict(index=0, line=get_lines(kwargs.get("lines"))[0])
    if not __is_service_parameters(**kwargs) or len(service_names) > 2:
        __write_sec_main(**kwargs)
        __write_sec_offset_row_col(**kwargs)
        __write_sec_offset_pattern(**kwargs)
        __write_sec_type(**kwargs)
        __write_sec_func(**kwargs)
        __write_sec_sub_fields(**kwargs)
        __write_service_fields(**kwargs)

    else:
        kwargs.get("file").write("pattern=@Прочие\n")
        kwargs.get("file").write("row_data=0\n")
        if __is_service_parameters(**kwargs):
            col = kwargs.get("lines")["dic"]["service"][0]["col"]
            kwargs.get("file").write(f"col_config={col}\n")
            if kwargs.get("sec_is_hash"):
                kwargs.get("file").write(f"func=hash\n")
    # kwargs.get("file").write("\n")
    return


def write_section(**kwargs):
    __write_section_head(**kwargs)
    kwargs["sec_prefix"] = __get_sec_prefix(**kwargs)
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix')}"
    )
    if (
        fld_param
        or kwargs.get("sec_func")
        or __is_sec_internal_id(**kwargs)
        or kwargs.get("sec_is_func_name")
        or "internal_id" in kwargs.get("sec_name")
    ):
        kwargs["line"] = __get_sub_fields(**kwargs)
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


def __is_service_parameters(**kwargs) -> bool:
    """Наименование услуг в разных строках одной колонки исходной таблицы
    Многострочный (иерархический) вариант записи исходных данных
    """
    return bool(kwargs.get("lines")["dic"].get("service"))


def __is_service_section(**kwargs) -> bool:
    """секция может быть многострочной. Т.е. содержать дочерние поля"""
    return (
        not kwargs.get("sec_is_service") is None
        and kwargs.get("sec_is_service") is False
    )


def __is_sub_fields_in_row(**kwargs) -> bool:
    """дочерние поля формируются из колонок исходной таблицы"""
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    return bool(fld_param) is True and len(fld_param) > 1

def __is_sub_fields_in_col(**kwargs) -> bool:
    if __is_sub_fields_in_row(**kwargs):
        # Если данные берктся только из нескольких колонок исходной таблицы
        return False
    if __is_service_section(**kwargs):
        # секция не является многострочной
        return False
    return True


def __get_fld_parameters(**kwargs):
    return kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )


def __get_service_col(**kwargs) -> int:
    """номер колонки с услугами если есть иначе 0"""
    return (
        kwargs.get("lines")["dic"]["service"][0]["col"]
        if __is_service_parameters(**kwargs)
        else 0
    )


def __get_filed_col(**kwargs) -> int:
    """номер колонки для поля, если поле задано в настройках иначе 0"""
    fld_param = __get_fld_parameters(**kwargs)
    service_field = kwargs.get("line")
    if service_field and service_field["line"].get("col"):
        return service_field["line"]["col"]
    if fld_param:
        return fld_param[0]["col"]
    return __get_service_col(**kwargs)


def __is_sec_internal_id(**kwargs) -> bool:
    return kwargs.get("sec_is_ident")



def __write_sec_main(**kwargs):
    # kwargs.get("file").write("pattern=@0\n")
    # kwargs.get("file").write("col_config=0\n")
    pass


def __write_sec_offset_row_col(**kwargs):
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    service_field = kwargs["line"]
    if __is_sub_fields_in_col(**kwargs) and __is_service_parameters(**kwargs):
        # если поле не однострочное и не содержит данных более чем из одной колонки исходной таблицы
        col_service =  __get_service_col(**kwargs)
        col_fld = __get_filed_col(**kwargs)

        if __is_sec_internal_id(**kwargs):
            kwargs.get("file").write("col_config=0\n")
            if not fld_param:
            # if col_fld != 0 and col_fld != col_service:
                kwargs.get("file").write(f"offset_col_config={col_fld}\n")
        else:
            kwargs.get("file").write(f"col_config={col_service}\n")
            if col_fld != col_service:
                kwargs.get("file").write(f"offset_col_config={col_fld}\n")

    else:
        if (
            fld_param
            and not __is_sec_internal_id(**kwargs)
            and not kwargs.get("sec_is_func_name")
        ):
            col = service_field["line"].get("col", fld_param[0]["col"])
            kwargs.get("file").write(f"col_config={col}\n")
        elif service_field is None or service_field["index"] == 0:
            kwargs.get("file").write("pattern=@0\n")
            kwargs.get("file").write("col_config=0\n")
        if service_field is None or service_field["index"] == 0:
            kwargs.get("file").write("row_data=0\n")


def __write_sec_offset_pattern(**kwargs):
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    service_field = kwargs["line"]
    if fld_param:
        pattern_default = ""
        if fld_param[0]["pattern"]:
            if service_field is None or service_field["index"] == 0:
                pattern_default = fld_param[0]["pattern"].strip()

        if __is_sub_fields_in_col(**kwargs):
            if (
                __is_service_parameters(**kwargs)
                or __is_sec_internal_id(**kwargs)
                or kwargs.get("sec_is_func_name")
            ):
                name = get_name(get_ident(service_field["line"]["name"].split(";")[0]))
                if __is_sec_internal_id(**kwargs):
                    if service_field is None or service_field["index"] == 0:
                        kwargs.get("file").write("pattern=@0\n")
                    kwargs.get("file").write(f"offset_pattern=@{name}\n")
                else:
                    kwargs.get("file").write(f"pattern=@{name}\n")
                    if service_field is None or service_field["index"] == 0:
                        col_service = kwargs.get("lines")["dic"]["service"][0]["col"]
                        if not fld_param:
                            col_fld = col_service
                        else:
                            col_fld = service_field["line"].get(
                                "col", fld_param[0]["col"]
                            )
                        if col_fld != col_service:
                            if pattern_default:
                                kwargs.get("file").write(
                                    f"offset_pattern={pattern_default}\n"
                                )
                            else:
                                kwargs.get("file").write(f"offset_pattern=.+\n")

            elif not __is_sec_internal_id(**kwargs) and not kwargs.get("sec_is_func_name"):
                if pattern_default:
                    kwargs.get("file").write(f"pattern={pattern_default}\n")
                else:
                    kwargs.get("file").write(f"pattern=.+\n")
        elif not __is_sec_internal_id(**kwargs) and not kwargs.get("sec_is_func_name"):
            if pattern_default:
                kwargs.get("file").write(f"pattern={pattern_default}\n")
            else:
                kwargs.get("file").write(f"pattern=.+\n")
    else:
        if __is_sub_fields_in_col(**kwargs) and kwargs.get("lines")["dic"].get(
            "service"
        ):
            name = get_name(get_ident(service_field["line"]["name"].split(";")[0]))
            if __is_sec_internal_id(**kwargs):
                if service_field is None or service_field["index"] == 0:
                    kwargs.get("file").write("pattern=@0\n")
                kwargs.get("file").write(f"offset_pattern=@{name}\n")
            else:
                kwargs.get("file").write(f"pattern=@{name}\n")


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
            if __is_sub_fields_in_col(**kwargs) and kwargs.get("lines")["dic"].get(
                "service"
            ):
                kwargs.get("file").write(f"offset_type={oft}\n")
            else:
                kwargs.get("file").write(f"type={oft}\n")


def __write_sec_func(**kwargs):
    service_field = kwargs["line"]
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    suffix = f'+{kwargs.get("sec_suffix")}' if kwargs.get("sec_suffix") else ""
    hash = ",hash" if kwargs.get("sec_is_hash") else ""
    dictionary = ",dictionary" if kwargs.get("sec_is_func_dictionary") else ""
    spacerepl = ",spacerepl" if not kwargs.get("sec_is_func_dictionary") else ""
    if (
        fld_param
        and fld_param[0]["func"]
        and (service_field is None or service_field["index"] == 0)
    ):
        func = fld_param[0]["func"][0]
        kwargs.get("file").write(f"func={func}\n")
    elif kwargs.get("sec_func") and (
        service_field is None or service_field["index"] == 0
    ):
        if kwargs.get("sec_func")[0] != "!":
            kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
        else:
            kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
            kwargs.get("file").write(f"func_is_no_return=true\n")
    elif __is_sec_internal_id(**kwargs) and not service_field is None:
        ident = get_func_name(service_field["line"]["name"].split(";")[0])
        func_ident = kwargs.get("sec_func_ident", "id")
        kwargs.get("file").write(
            f"func={func_ident}+{ident}{suffix}{spacerepl}{hash}{dictionary}\n"
        )
    elif kwargs.get("sec_is_func_name") and not service_field is None:
        if (
            fld_param
            and not __is_sub_fields_in_col(**kwargs)
            and (
                kwargs.get("sec_is_func_name_no_ident") is None
                or kwargs.get("sec_is_func_name_no_ident")
            )
        ):
            ident = get_ident(
                get_func_name(service_field["line"]["name"].split(";")[0])
            )
        else:
            ident = get_func_name(service_field["line"]["name"].split(";")[0])
        kwargs.get("file").write(f"func={ident}{hash}{dictionary}\n")
    elif (
        fld_param
        and __is_sub_fields_in_col(**kwargs)
        and __is_service_parameters(**kwargs)
        and (service_field is None or service_field["index"] == 0)
    ):
        col_fld = service_field["line"].get("col", fld_param[0]["col"])
        col_service = kwargs.get("lines")["dic"]["service"][0]["col"]


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

            kwargs["line"] = dict(index=i + 1, line=line)
            kwargs["line"]["line"]["name"] = get_ident(kwargs["line"]["line"]["name"])
            __write_sec_offset_row_col(**kwargs)
            __write_sec_func(**kwargs)

            # if line["func"]:
            #     kwargs.get("file").write(f'func={line["func"][0]}\n')
            # elif kwargs.get("sec_func"):
            #     if kwargs.get("sec_func")[0] != "!":
            #         kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
            #     else:
            #         kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
            #         kwargs.get("file").write(f"func_is_no_return=true\n")


def __write_service_fields(**kwargs):
    if __is_sub_fields_in_col(**kwargs):
        service_names: list = get_lines(kwargs.get("lines"))
        for i, line in enumerate(service_names[1:]):
            if (
                __is_service_parameters(**kwargs)
                or __is_sec_internal_id(**kwargs)
                or kwargs.get("sec_is_func_name")
            ):
                kwargs.get("file").write(
                    f"\n[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
                )
                kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")

                kwargs["line"] = dict(index=i + 1, line=line)
                __write_sec_offset_pattern(**kwargs)
                __write_sec_func(**kwargs)


def __get_sub_fields(**kwargs):
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    if __is_sub_fields_in_col(**kwargs):
        kwargs["line"] = dict(index=0, line=get_lines(kwargs.get("lines"))[0])
    else:
        if fld_param:
            kwargs["line"] = dict(index=0, line=fld_param[0])
            kwargs["line"]["line"]["name"] = get_ident(kwargs["line"]["line"]["name"])
        else:
            kwargs["line"] = None
    return kwargs["line"]
