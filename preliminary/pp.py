from sections import *


def pp(lines: list, path: str):

    file_name = f"{path}/ini/3_pp.ini"
    with open(file_name, "w") as file:

        doc_type = "pp"
        required_fields = (
            ",".join(lines["required"]["required_pp"])
            if lines["required"].get("required_pp")
            else "bill_value,payment_value,credit,saldo"
        )
        write_section_caption(**dict(file=file, sec_type=doc_type))
        write_section_doc(
            **dict(
                file=file,
                sec_type="doc",
                sec_number=1,
                sec_title="Платежный документ",
                sec_name=doc_type,
                required_fields=required_fields,
            )
        )

        write_section_org_ppa_guid(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=0,
                sec_title="ИНН, ОГРН или OrgID",
                sec_name="org_ppa_guid",
            )
        )

        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=1,
                sec_title="Внутренний идентификатор ПД",
                sec_name="internal_id",
                sec_suffix="ПУ",
                sec_is_service=False,
                sec_is_hash=True,
                sec_is_ident=True,
                sec_is_func_name_no_ident=False,
                sec_func="id+account_number,spacerepl,hash",
            )
        )

        write_section_account_internal_id(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=2,
                sec_title="Внутренний идентификатор ЛС",
                sec_name="account_internal_id",
            )
        )

        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=3,
                sec_title="ГИС. Идентификатор ПП GUID",
                sec_name="gis_id",
                required_fields=required_fields,
            )
        )

        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=4,
                sec_title="Месяц (первый день месяца)",
                sec_name="month",
                required_fields=required_fields,
                sec_func="period_first",
                sec_is_service=False,
            )
        )

        file.write("[pp_5]\n")
        file.write("; Сальдо на начало месяца (<0 переплата, >0 задолженность)\n")
        file.write("name=credit\n")
        if lines["dic"].get("credit"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(f'offset_col_config={lines["dic"]["credit"][0]["col"]}\n')
            file.write("offset_type=float\n")
            file.write("offset_pattern=@currency\n")
            file.write("func=round2\n\n")

        file.write("[pp_6]\n")
        file.write("; Сальдо на конец месяца (<0 переплата, >0 задолженность)\n")
        file.write("name=saldo\n")
        if lines["dic"].get("saldo"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(f'offset_col_config={lines["dic"]["saldo"][0]["col"]}\n')
            file.write("offset_type=float\n")
            file.write("offset_pattern=@currency\n")
            file.write("func=round2\n\n")

        file.write("[pp_7]\n")
        file.write("; Оплачено денежных средств в расчетный период\n")
        file.write("name=payment_value\n")
        if lines["dic"].get("payment_value"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(f'offset_col_config={lines["dic"]["payment_value"][0]["col"]}\n')
            file.write("offset_type=float\n")
            file.write("offset_pattern=@currency\n")
            file.write("func=round2\n\n")

        file.write("[pp_8]\n")
        file.write(
            "; Учтены платежи, поступившие до указанного числа расчетного периода включительно\n"
        )
        file.write("name=payment_date\n")
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        if lines["dic"].get("payment_date"):
            file.write(f'offset_col_config={lines["dic"]["payment_date"][0]["col"]}\n')
            file.write("offset_pattern=.+\n")
        else:
            file.write("func=period_last\n")
        file.write("depends_on=payment_value\n")
        file.write("\n")

        file.write("[pp_9]\n")
        file.write("; Сумма счета, учетом задолженности/переплаты\n")
        file.write("name=bill_value\n")
        if lines["dic"].get("bill_value"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(f'offset_col_config={lines["dic"]["bill_value"][0]["col"]}\n')
            file.write("offset_type=float\n")
            file.write("offset_pattern=@currency\n")
            file.write("func=round2\n\n")

        file.write("[pp_10]\n")
        file.write("; Номер расчетного счета\n")
        file.write("name=account_number\n")
        if lines["dic"].get("account_number_pp"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["account_number_pp"][0]["col"]}\n'
            )
            if lines["dic"]["account_number_pp"][0]["pattern"]:
                file.write(
                    f'offset_pattern={lines["dic"]["account_number_pp"][0]["pattern"]}\n'
                )
            else:
                file.write("offset_pattern=.+\n")
        else:
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write("pattern=@0\n")
            file.write(f"offset_col_config=0\n")
            file.write("offset_pattern=@0\n")
            file.write(f"func=account_number\n")
            file.write("func_is_no_return=true\n")
        file.write("\n")
        # bank_bik
        file.write("[pp_11]\n")
        file.write("; БИК банка\n")
        file.write("name=bank_bik\n")
        if lines["dic"].get("bank_bik"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write(f'offset_col_config={lines["dic"]["bank_bik"][0]["col"]}\n')
            if lines["dic"]["bank_bik"][0]["pattern"]:
                file.write(f'offset_pattern={lines["dic"]["bank_bik"][0]["pattern"]}\n')
            else:
                file.write("offset_pattern=.+\n")
        else:
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write(f"offset_col_config=0\n")
            file.write("offset_pattern=@0\n")
            file.write(f"func=bik,spacerepl\n")
            file.write("func_is_no_return=true\n")

        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=12,
                sec_title="Тип лицевого счета (uo|cr)",
                sec_name="account_type",
                sec_is_service=False,
            )
        )

    return file_name
