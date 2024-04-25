from sections import *


def contract(lines: list, path: str, sec_number:int) -> str:
    doc_type = "contracts"
    file_name = f"{path}/ini/8_contracts.ini"
    with open(file_name, "w") as file:
        required_fields = (
            ",".join(lines["required"]["required_contracts"])
            if lines["required"].get("required_contracts")
            and len(lines["required"].get("required_contracts")) != 0
            and lines["required"].get("required_contracts")[0]
            else "offer,start_date"
        )

        write_section_caption(**dict(file=file, sec_type=doc_type))
        write_section_doc(
            **dict(
                file=file,
                sec_type="doc",
                sec_number=sec_number,
                sec_title="Договоры",
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
                sec_title="Внутренний идентификатор договора",
                sec_name="internal_id",
                sec_func="_+К,spacerepl,hash",
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
                sec_title="Номер договора",
                sec_name="contract_number",
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
                sec_title="номера internal_id  из pp_service,через запятую, которые относятся к этому договору",
                sec_name="services",
                sec_func="services",
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
                sec_title="Дата начала договора",
                sec_name="start_date",
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
                sec_title="Дата завершения договора",
                sec_name="stop_date",
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
                sec_title="ГИС. Идентификатор договора",
                sec_name="gis_contract_id",
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
                sec_title="ОГРН организации, если договор с ЮЛ",
                sec_name="ogrn",
                sec_is_service=False,
            )
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
            sec_title="договор оферты. договор оферты, да/нет/пусто (если нет данных)",
            sec_name="offer",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
            sec_title="срок представления (выставления) платежных документов, не позднее",
            sec_name="billing_day",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
            sec_title="срок внесения платы, не позднее",
            sec_name="payment_day",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
            sec_title="число начала подачи показаний счетчиков",
            sec_name="period_from",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
            sec_title="число завершения подачи показаний счетчиков",
            sec_name="period_to",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
            sec_title="ИНН организации, если договор с ЮЛ",
            sec_name="inn",
            sec_is_service=False,
        )
        sec_number += 1
        write_other_fields(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
        )
        sec_number += 1
    return file_name
