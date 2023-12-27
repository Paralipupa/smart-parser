from sections import *

def pp(lines: list, path: str):
    doc_type = "pp"
    file_name = f"{path}/ini/3_pp.ini"
    with open(file_name, "w") as file:
        file.write(
            ";########################################################################################################################\n"
        )
        file.write(
            ";---------------------------------------------------------------- pp ----------------------------------------------------\n"
        )
        file.write(
            ";########################################################################################################################\n"
        )
        file.write("[doc_1]\n")
        file.write("; Платежный документ \n")
        file.write("name=pp\n")
        if lines["required"].get("required_pp"):
            file.write(f'required_fields={",".join(lines["required"]["required_pp"])}\n\n')
        else:
            file.write("required_fields=bill_value,payment_value,credit,saldo\n\n")

        file.write("[pp_0]\n")
        file.write(";ИНН, ОГРН или OrgID\n")
        file.write("name=org_ppa_guid\n")
        file.write("pattern=@\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        file.write("func=inn\n\n")

        file.write("[pp_1]\n")
        file.write("; Внутренний идентификатор ПД\n")
        file.write("name=internal_id\n")
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        file.write("func=id+account_number,spacerepl,hash\n\n")

        file.write("[pp_2]\n")
        file.write("; Внутренний идентификатор ЛС\n")
        file.write("name=account_internal_id\n")
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        if lines["dic"].get("account_internal_id"):
            file.write(
                f'offset_col_config={lines["dic"]["account_internal_id"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
        file.write("func=spacerepl,hash\n")
        file.write("\n")

        file.write("[pp_3]\n")
        file.write("; ГИС. Идентификатор ПП\n")
        file.write("name=gis_id\n\n")

        file.write("[pp_4]\n")
        file.write("; Месяц (первый день месяца)\n")
        file.write("name=month\n")
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        file.write("func=period_first\n\n")

        file.write("[pp_5]\n")
        file.write("; Сальдо на начало месяца (<0 переплата, >0 задолженность)\n")
        file.write("name=credit\n")
        if lines["dic"].get("credit"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["credit"][0]["col"]}\n'
            )
            file.write("offset_type=float\n")
            file.write("offset_pattern=@currency\n")
            file.write("func=round2\n\n")

        file.write("[pp_6]\n")
        file.write("; Сальдо на конец месяца (<0 переплата, >0 задолженность)\n")
        file.write("name=saldo\n")
        if lines["dic"].get("saldo"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["saldo"][0]["col"]}\n'
            )
            file.write("offset_type=float\n")
            file.write("offset_pattern=@currency\n")
            file.write("func=round2\n\n")

        file.write("[pp_7]\n")
        file.write("; Оплачено денежных средств в расчетный период\n")
        file.write("name=payment_value\n")
        if lines["dic"].get("payment_value"):
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"]["payment_value"][0]["col"]}\n'
            )
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
            file.write(
                f'offset_col_config={lines["dic"]["payment_date"][0]["col"]}\n'
            )
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
            file.write(
                f'offset_col_config={lines["dic"]["bill_value"][0]["col"]}\n'
            )
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
            file.write(
                f'offset_col_config={lines["dic"]["bank_bik"][0]["col"]}\n'
            )
            if lines["dic"]["bank_bik"][0]["pattern"]:
                file.write(
                    f'offset_pattern={lines["dic"]["bank_bik"][0]["pattern"]}\n'
                )
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
        file.write("\n")
        file.write("\n")

        write_section(file, lines, doc_type, 12,
                        "Тип лицевого счета (uo|cr)", "account_type")

    return file_name
