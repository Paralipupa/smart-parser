import re
from utils import get_ident, get_name, get_lines, get_func_name
from settings import *


def write_other_fields(**kwargs):
    for item in __get_other_fields(**kwargs):
        for fld in item["fields"]:
            name = re.findall("(?<=\().+(?=\))", fld["name"])
            key = re.findall(".+(?=\()", fld["name"])
            title = item["name"]
            if key and title and name and kwargs.get("sec_type") == name[0]:
                kwargs["sec_name"] = key[0]
                kwargs["sec_title"] = title
                kwargs.get("file").write("\n")
                write_section_doc(**kwargs)
                pattern = ".+"
                if fld.get("pattern"):
                    pattern = fld["pattern"]
                kwargs.get("file").write(f"pattern={pattern}\n")
                kwargs.get("file").write(f"col_config={fld['col']}\n")
                kwargs.get("file").write("row_data=0\n")
                if fld.get("func"):
                    func = __get_func(fld["func"][0], **kwargs)
                    kwargs.get("file").write(f"func={func}\n")
                kwargs["sec_number"] += 1


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
    if kwargs.get("sec_type") == "doc":
        if kwargs.get("lines") and kwargs["lines"]["type"].get(
            f"type_{kwargs.get('sec_name')}"
        ):
            kwargs.get("file").write(
                "type="
                + kwargs["lines"]["type"].get(f"type_{kwargs.get('sec_name')}")[0]
                + "\n"
            )
    if kwargs.get("required_fields"):
        kwargs.get("file").write(f"required_fields={kwargs.get('required_fields')}\n")
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
    kwargs["sec_prefix"] = __get_sec_prefix(**kwargs)
    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
        kwargs.get("file").write("pattern=.+\n")
        col = kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["col"]
        kwargs.get("file").write(f"col_config={col}\n")
        kwargs.get("file").write("row_data=0\n")
        if (
            kwargs.get("lines")["dic"].get(
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            )
            and kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["func"]
        ):
            func = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["func"][0]
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
    kwargs.get("file").write("row_data=0\n")
    kwargs["sec_prefix"] = __get_sec_prefix(**kwargs)

    if kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    ):
        col = kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["col"]
        kwargs.get("file").write(f"col_config={col}\n")
        if kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["pattern"]:
            pattern = kwargs.get("lines")["dic"][
                f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
            ][0]["pattern"]
            kwargs.get("file").write(f"pattern={pattern}\n")
        else:
            kwargs.get("file").write("pattern=.+\n")
    else:
        kwargs.get("file").write("pattern=@0\n")
        kwargs.get("file").write("col_config=0\n")

    if (
        kwargs.get("lines")["dic"].get(
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        )
        and kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["func"]
    ):
        func = kwargs.get("lines")["dic"][
            f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
        ][0]["func"][0]
        kwargs.get("file").write(f"func={func}\n")
    else:
        kwargs.get("file").write("func=spacerepl,hash\n")
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
            kwargs.get("file").write(f"col_config={__get_service_col(**kwargs)}\n")
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


def write_section_bank(**kwargs):
    __write_section_head(**kwargs)
    __write_sec_main(**kwargs)
    kwargs.get("file").write(f"row_data=0\n")
    fld_param = __get_fld_parameters(**kwargs)
    if fld_param and fld_param[0].get("col") != 0:
        kwargs.get("file").write(f"offset_col_config={fld_param[0].get('col')}\n")
        kwargs.get("file").write(
            f"offset_pattern={fld_param[0].get('pattern') if fld_param[0].get('pattern') else '.+' }\n"
        )
    else:
        kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
        kwargs.get("file").write("func_is_no_return=true\n")


def write_section_date_payment(**kwargs):
    __write_section_head(**kwargs)
    __write_sec_main(**kwargs)
    kwargs.get("file").write(f"row_data=0\n")
    fld_param = __get_fld_parameters(**kwargs)
    if fld_param:
        kwargs.get("file").write(f"offset_col_config={fld_param[0].get('col')}\n")
        kwargs.get("file").write("offset_pattern=.+\n")
    else:
        kwargs.get("file").write("func=period_last\n")
        kwargs.get("file").write("depends_on=payment_value\n")


def __write_section_service_internal_id(**kwargs):
    service_names: list = get_lines(kwargs.get("lines"))
    kwargs["line"] = dict(index=0, line=get_lines(kwargs.get("lines"))[0])
    if not __is_service_parameters(**kwargs) or len(service_names) > 2:
        __write_sec_row_col(**kwargs)
        __write_sec_pattern(**kwargs)
        __write_sec_type(**kwargs)
        __write_sec_func(**kwargs)
        __write_sec_sub_fields(**kwargs)
        __write_service_fields(**kwargs)

    else:
        kwargs.get("file").write("pattern=@Прочие\n")
        kwargs.get("file").write("row_data=0\n")
        if __is_service_parameters(**kwargs):
            col_service = __get_service_col(**kwargs)
            kwargs.get("file").write(f"col_config={col_service}\n")
            if kwargs.get("sec_is_hash"):
                kwargs.get("file").write(f"func=hash\n")
    # kwargs.get("file").write("\n")
    return


def write_section_calculation(**kwargs):
    __write_section_head(**kwargs)
    fld_param = __get_fld_parameters(**kwargs)
    if fld_param:
        __write_sec_main(**kwargs)
        kwargs.get("file").write(f"offset_col_config={fld_param[0].get('col')}\n")
        kwargs.get("file").write(
            f"offset_type={fld_param[0].get('type')[0] if fld_param[0].get('type') else 'float'}\n"
        )
        kwargs.get("file").write(
            f"offset_pattern={fld_param[0].get('pattern') if fld_param[0].get('pattern') else '@currency' }\n"
        )
        func = __get_func(
            fld_param[0].get("func")[0] if fld_param[0].get("func") else "round2",
            **kwargs,
        )
        kwargs.get("file").write(f"func={func} \n")


def write_section(**kwargs):
    __write_section_head(**kwargs)
    kwargs["sec_prefix"] = __get_sec_prefix(**kwargs)
    fld_param = __get_fld_parameters(**kwargs)
    if (
        fld_param
        or kwargs.get("sec_func")
        or __is_sec_internal_id(**kwargs)
        or __is_sec_as_service_name(**kwargs)
        or "internal_id" in kwargs.get("sec_name")
    ):
        kwargs["line"] = __get_sub_fields(**kwargs)
        __write_sec_row_col(**kwargs)
        __write_sec_pattern(**kwargs)
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


def __is_simple_section(**kwargs) -> bool:
    """Простая секция без дочерних полей"""
    return (
        not kwargs.get("sec_is_service") is None
        and kwargs.get("sec_is_service") is False
    )


def __is_sub_fields_in_row(**kwargs) -> bool:
    """дочерние поля формируются из колонок исходной таблицы"""
    fld_param = __get_fld_parameters(**kwargs)
    return bool(fld_param) is True and len(fld_param) > 1


def __is_sub_fields_in_col(**kwargs) -> bool:
    if __is_sub_fields_in_row(**kwargs):
        # Если данные берктся только из нескольких колонок исходной таблицы
        return False
    if __is_simple_section(**kwargs):
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


def __get_field_col(**kwargs) -> int:
    """номер колонки для поля, если поле задано в настройках иначе 0"""
    current_service = __get_current_service(**kwargs)
    if current_service and current_service["line"].get("col"):
        return current_service["line"]["col"]
    fld_param = __get_fld_parameters(**kwargs)
    if fld_param:
        return fld_param[0]["col"]
    return __get_service_col(**kwargs)


def __is_sec_internal_id(**kwargs) -> bool:
    return kwargs.get("sec_is_ident")


def __is_sec_as_service_name(**kwargs) -> bool:
    return kwargs.get("sec_is_func_name")


def __get_current_service(**kwargs) -> list:
    return kwargs.get("line")


def __is_first_service(**kwargs) -> bool:
    current_service = __get_current_service(**kwargs)
    return current_service is None or current_service["index"] == 0


def __write_sec_main(**kwargs):
    kwargs.get("file").write("pattern=@0\n")
    kwargs.get("file").write("col_config=0\n")


def __write_sec_row_col(**kwargs):
    fld_param = __get_fld_parameters(**kwargs)
    col_fld = __get_field_col(**kwargs)
    if __is_sub_fields_in_col(**kwargs) and __is_service_parameters(**kwargs):
        # если поле не однострочное и не содержит данных более чем из одной колонки исходной таблицы
        col_service = __get_service_col(**kwargs)

        if __is_sec_internal_id(**kwargs):
            if col_fld != col_service:
                kwargs.get("file").write(f"col_config={col_fld}\n")
            else:
                kwargs.get("file").write("col_config=0\n")
            if col_fld != 0:
                kwargs.get("file").write(f"offset_col_config={col_service}\n")
        else:
            kwargs.get("file").write(f"col_config={col_service}\n")
            if col_fld != col_service:
                kwargs.get("file").write(f"offset_col_config={col_fld}\n")

    else:
        if (
            fld_param
            and not __is_sec_internal_id(**kwargs)
            and not __is_sec_as_service_name(**kwargs)
        ):
            kwargs.get("file").write(f"col_config={col_fld}\n")
        elif __is_first_service(**kwargs):
            pattern_default = __get_pattern_default(**kwargs)
            if not pattern_default:
                kwargs.get("file").write("pattern=@0\n")
            kwargs.get("file").write("col_config=0\n")
        if __is_first_service(**kwargs) and (
            not __is_service_parameters(**kwargs) or __is_simple_section(**kwargs)
        ):
            kwargs.get("file").write("row_data=0\n")


def __write_sec_pattern(**kwargs):
    fld_param = __get_fld_parameters(**kwargs)
    current_service = __get_current_service(**kwargs)
    if fld_param:
        pattern_default = __get_pattern_default(**kwargs)
        col_fld = __get_field_col(**kwargs)
        if __is_sub_fields_in_col(**kwargs):
            if (
                __is_service_parameters(**kwargs)
                or __is_sec_internal_id(**kwargs)
                or __is_sec_as_service_name(**kwargs)
            ):
                name = get_name(
                    get_ident(current_service["line"]["name"].split(";")[0])
                )
                if __is_sec_internal_id(**kwargs):
                    if __is_first_service(**kwargs):
                        kwargs.get("file").write("pattern=@0\n")
                    if col_fld != 0:
                        kwargs.get("file").write(f"offset_pattern=@{name}\n")
                else:
                    kwargs.get("file").write(f"pattern=@{name}\n")
                    if __is_first_service(**kwargs):
                        col_service = __get_service_col(**kwargs)
                        if col_fld != col_service:
                            if pattern_default:
                                kwargs.get("file").write(
                                    f"offset_pattern={pattern_default}\n"
                                )
                            else:
                                kwargs.get("file").write(f"offset_pattern=.+\n")

            elif not __is_sec_internal_id(**kwargs) and not kwargs.get(
                "sec_is_func_name"
            ):
                if pattern_default:
                    kwargs.get("file").write(f"pattern={pattern_default}\n")
                else:
                    kwargs.get("file").write(f"pattern=.+\n")
        elif not __is_sec_internal_id(**kwargs) and not __is_sec_as_service_name(
            **kwargs
        ):
            if pattern_default:
                kwargs.get("file").write(f"pattern={pattern_default}\n")
            else:
                kwargs.get("file").write(f"pattern=.+\n")
        elif pattern_default:
            kwargs.get("file").write(f"pattern={pattern_default}\n")

    else:
        if __is_sub_fields_in_col(**kwargs) and kwargs.get("lines")["dic"].get(
            "service"
        ):
            name = get_name(get_ident(current_service["line"]["name"].split(";")[0]))
            if __is_sec_internal_id(**kwargs):
                if __is_first_service(**kwargs):
                    kwargs.get("file").write("pattern=@0\n")
                col_fld = __get_field_col(**kwargs)
                if col_fld != 0:
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


def __get_func(func, **kwargs):
    columns = [
        (x[0]["col"], key)
        for key, x in kwargs["lines"]["dic"].items()
        if x and f"({key})" in func
    ]
    if columns:
        func = func.replace(columns[0][1], str(columns[0][0]))
    return func


def __write_sec_func(**kwargs):
    current_service = __get_current_service(**kwargs)
    fld_param = __get_fld_parameters(**kwargs)
    suffix = f'+{kwargs.get("sec_suffix")}' if kwargs.get("sec_suffix") else ""
    hash = ",hash" if kwargs.get("sec_is_hash") else ""
    dictionary = ",dictionary" if kwargs.get("sec_is_func_dictionary") else ""
    spacerepl = ",spacerepl" if not kwargs.get("sec_is_func_dictionary") else ""
    if fld_param and fld_param[0]["func"] and __is_first_service(**kwargs):
        func = __get_func(fld_param[0]["func"][0], **kwargs)
        kwargs.get("file").write(f"func={func}\n")
    elif kwargs.get("sec_func") and __is_first_service(**kwargs):
        if kwargs.get("sec_func")[0] != "!":
            kwargs.get("file").write(f"func={kwargs.get('sec_func')}\n")
        else:
            kwargs.get("file").write(f"func={kwargs.get('sec_func')[1:]}\n")
            kwargs.get("file").write(f"func_is_no_return=true\n")
        if kwargs.get("sec_func_pattern"):
            kwargs.get("file").write(f"func_pattern={kwargs.get('sec_func_pattern')}\n")
    elif __is_sec_internal_id(**kwargs) and not current_service is None:
        ident = get_func_name(current_service["line"]["name"].split(";")[0])
        if current_service["line"]["name"] == "Прочие" and __is_service_parameters(
            **kwargs
        ):
            ident = "_"
        if not (fld_param and fld_param[0]["func"]):
            func_ident = kwargs.get("sec_func_ident", "id")
            kwargs.get("file").write(
                f"func={func_ident}+{ident}{suffix}{spacerepl}{hash}{dictionary}\n"
            )
            if kwargs.get("sec_func_pattern") and __is_first_service(**kwargs):
                kwargs.get("file").write(
                    f"func_pattern={kwargs.get('sec_func_pattern')}\n"
                )
    elif __is_sec_as_service_name(**kwargs) and not current_service is None:
        if (
            fld_param
            and not __is_sub_fields_in_col(**kwargs)
            and (
                kwargs.get("sec_is_func_name_no_ident") is None
                or kwargs.get("sec_is_func_name_no_ident")
            )
        ):
            ident = get_ident(
                get_func_name(current_service["line"]["name"].split(";")[0])
            )
        else:
            ident = get_func_name(current_service["line"]["name"].split(";")[0])
        if current_service["line"]["name"] == "Прочие" and __is_service_parameters(
            **kwargs
        ):
            ident = "_"
        kwargs.get("file").write(f"func={ident}{hash}{dictionary}\n")


def __write_sec_sub_fields(**kwargs):
    fld_param = __get_fld_parameters(**kwargs)
    if fld_param:
        for i, line in enumerate(fld_param[1:]):
            kwargs.get("file").write(
                f"[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
            )
            kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")

            kwargs["line"] = dict(index=i + 1, line=line)
            kwargs["line"]["line"]["name"] = get_ident(kwargs["line"]["line"]["name"])
            __write_sec_row_col(**kwargs)
            __write_sec_func(**kwargs)


def __write_service_fields(**kwargs):
    if __is_sub_fields_in_col(**kwargs):
        service_names: list = get_lines(kwargs.get("lines"))
        for i, line in enumerate(service_names[1:]):
            if (
                __is_service_parameters(**kwargs)
                or __is_sec_internal_id(**kwargs)
                or __is_sec_as_service_name(**kwargs)
            ):
                kwargs.get("file").write(
                    f"\n[{kwargs.get('sec_type')}_{kwargs.get('sec_number')}_{i}]\n"
                )
                kwargs.get("file").write(f"; {kwargs.get('sec_title')}\n")

                kwargs["line"] = dict(index=i + 1, line=line)
                __write_sec_pattern(**kwargs)
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


def __get_pattern_default(**kwargs):
    fld_param = kwargs.get("lines")["dic"].get(
        f"{kwargs.get('sec_name')}{kwargs.get('sec_prefix','')}"
    )
    if fld_param:
        if fld_param[0]["pattern"]:
            if __is_first_service(**kwargs):
                return fld_param[0]["pattern"].strip()
    return ""


def __get_other_fields(**kwargs):
    return kwargs["lines"]["fields"]
