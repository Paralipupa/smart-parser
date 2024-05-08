from sections import *


def pp(lines: list, path: str, sec_number: int):

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
                lines=lines,
                sec_type="doc",
                sec_number=sec_number,
                sec_title="Платежный документ",
                sec_name=doc_type,
                required_fields=required_fields,
            )
        )

        sec_number = 0
        write_section_org_ppa_guid(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="ИНН, ОГРН или OrgID",
                sec_name="org_ppa_guid",
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Внутренний идентификатор ПД",
                sec_name="internal_id",
                sec_is_service=False,
                sec_is_hash=True,
                sec_is_ident=True,
                sec_is_func_name_no_ident=False,
                sec_func="id+account_number,spacerepl,hash",
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Внутренний идентификатор ЛС",
                sec_name="account_internal_id",
                sec_func=(
                    ("id," if lines["param"].get("pattern_id_length") else "")
                    + "spacerepl,hash"
                ),
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="ГИС. Идентификатор ПП GUID",
                sec_name="gis_id",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Месяц (первый день месяца)",
                sec_name="month",
                required_fields=required_fields,
                sec_func="period_first",
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Сальдо на начало месяца (<0 переплата, >0 задолженность)",
                sec_name="credit",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Сальдо на конец месяца (<0 переплата, >0 задолженность)",
                sec_name="saldo",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Оплачено денежных средств в расчетный период",
                sec_name="payment_value",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section_date_payment(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Учтены платежи, поступившие до указанного числа расчетного периода включительно",
                sec_name="payment_date",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section_calculation(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Сумма счета, учетом задолженности/переплаты",
                sec_name="bill_value",
                required_fields=required_fields,
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Номер расчетного счета",
                sec_name="account_number",
                required_fields=required_fields,
                sec_func="!account_number",
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="БИК банка",
                sec_name="bank_bik",
                required_fields=required_fields,
                sec_func="!bik,spacerepl",
                sec_is_service=False,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Тип лицевого счета (uo|cr)",
                sec_name="account_type",
                sec_is_service=False,
            )
        )
        sec_number += 1
        write_other_fields(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
        )

    return file_name
