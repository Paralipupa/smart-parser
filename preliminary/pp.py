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
                sec_is_service=False,
                sec_is_hash=True,
                sec_is_ident=True,
                sec_is_func_name_no_ident=False,
                sec_func="id+account_number,spacerepl,hash",
            )
        )

        # write_section_account_internal_id(
        #     **dict(
        #         file=file,
        #         lines=lines,
        #         sec_type=doc_type,
        #         sec_number=2,
        #         sec_title="Внутренний идентификатор ЛС",
        #         sec_name="account_internal_id",
        #         sec_func=(
        #             ("id," if lines["param"].get("pattern_id_length") else "")
        #             + "spacerepl,hash"
        #         ),
        #     )
        # )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=2,
                sec_title="Внутренний идентификатор ЛС",
                sec_name="account_internal_id",
                sec_func=(
                    ("id," if lines["param"].get("pattern_id_length") else "")
                    + "spacerepl,hash"
                ),
                sec_is_service=False,
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
                sec_is_service=False,
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

        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=5,
                sec_title="Сальдо на начало месяца (<0 переплата, >0 задолженность)",
                sec_name="credit",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=6,
                sec_title="Сальдо на конец месяца (<0 переплата, >0 задолженность)",
                sec_name="saldo",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=7,
                sec_title="Оплачено денежных средств в расчетный период",
                sec_name="payment_value",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        write_section_date_payment(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=8,
                sec_title="Учтены платежи, поступившие до указанного числа расчетного периода включительно",
                sec_name="payment_date",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )
        
        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=9,
                sec_title="Сумма счета, учетом задолженности/переплаты",
                sec_name="bill_value",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=10,
                sec_title="Номер расчетного счета",
                sec_name="account_number",
                required_fields=required_fields,
                sec_func="!account_number",
                sec_is_service=False,
            )
        )

        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=11,
                sec_title="БИК банка",
                sec_name="bank_bik",
                required_fields=required_fields,
                sec_func="!bik,spacerepl",
                sec_is_service=False,
            )
        )

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
        write_other_fields(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=13,
        )

    return file_name
