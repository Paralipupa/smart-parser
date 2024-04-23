from sections import *


def contract(lines: list, path: str, sec_number:int) -> str:
    doc_type = "contract"
    file_name = f"{path}/ini/8_contract.ini"
    with open(file_name, "w") as file:
        required_fields = (
            ",".join(lines["required"]["required_contract"])
            if lines["required"].get("required_contract")
            and len(lines["required"].get("required_contract")) != 0
            and lines["required"].get("required_contract")[0]
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
        write_section_org_ppa_guid(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=0,
                sec_title="ИНН, ОГРН или OrgID",
                sec_name="org_ppa_guid",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=1,
                sec_title="Внутренний идентификатор договора",
                sec_name="internal_id",
                sec_func="_+К,spacerepl,hash",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=2,
                sec_title="номера internal_id  из pp_service,через запятую, которые относятся к этому договору",
                sec_name="services",
                sec_func="services",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=3,
                sec_title="Дата начала договора",
                sec_name="start_date",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=4,
                sec_title="Дата завершения договора",
                sec_name="stop_date",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=5,
                sec_title="ГИС. Идентификатор договора",
                sec_name="gis_contract_id",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=6,
                sec_title="ОГРН организации, если договор с ЮЛ",
                sec_name="ogrn",
                sec_is_service=False,
            )
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=7,
            sec_title="договор оферты. договор оферты, да/нет/пусто (если нет данных)",
            sec_name="offer",
            sec_is_service=False,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=8,
            sec_title="срок представления (выставления) платежных документов, не позднее",
            sec_name="billing_day",
            sec_is_service=False,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=9,
            sec_title="срок внесения платы, не позднее",
            sec_name="payment_day",
            sec_is_service=False,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=10,
            sec_title="число начала подачи показаний счетчиков",
            sec_name="period_from",
            sec_is_service=False,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=11,
            sec_title="число завершения подачи показаний счетчиков",
            sec_name="period_to",
            sec_is_service=False,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=12,
            sec_title="ИНН организации, если договор с ЮЛ",
            sec_name="inn",
            sec_func="inn",
            sec_is_service=False,
        )
        write_other_fields(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=13,
        )
    return file_name
