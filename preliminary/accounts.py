from sections import *


def accounts(lines: list, path: str, sec_number:int) -> str:
    doc_type = "accounts"
    file_name = f"{path}/ini/2_accounts.ini"
    with open(file_name, "w") as file:
        required_fields = (
            ",".join(lines["required"]["required_accounts"])
            if lines["required"].get("required_accounts")
            else "address,account_number,living_person_number,total_square"
        )

        write_section_caption(**dict(file=file, sec_type=doc_type))
        write_section_doc(
            **dict(
                file=file,
                lines=lines,
                sec_type="doc",
                sec_number=sec_number,
                sec_title="Лицевые счета",
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
                sec_number=1,
                sec_title="Внутренний идентификатор договора",
                sec_name="contract_internal_id",
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
                sec_number=2,
                sec_title="Внутренний идентификатор ЛС",
                sec_name="internal_id",
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
                sec_number=3,
                sec_title="Идентификатор дома GUID",
                sec_name="fias",
                sec_func="!fias",
                sec_is_service=False,
            )
        )
        sec_number += 1
        write_section_address(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=4,
                sec_title="Адрес дома",
                sec_name="address",
                sec_is_service=False,
            )
        )
        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=5,
                sec_title="Номер помещения (если есть)",
                sec_name="room_number",
                sec_is_service=False,
            )
        )
        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=6,
                sec_title="ГИС. Идентификатор квартиры GUID",
                sec_name="gis_premises_id",
                sec_is_service=False,
            )
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=7,
            sec_title="ГИС. Идентификатор блока GUID",
            sec_name="gis_block_id",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=8,
            sec_title="ГИС. Идентификатор комнаты GUID",
            sec_name="gis_room_id",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=9,
            sec_title="ГИС. Идентификатор ЛС GUID",
            sec_name="gis_account_id",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=10,
            sec_title="Номер ЛС",
            sec_name="account_number",
            sec_func="spacerepl",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=11,
            sec_title="ГИС. Идентификатор ЛС (20)",
            sec_name="gis_account_service_id",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=12,
            sec_title="ГИС. Номер ЛИ (20)",
            sec_name="gis_account_unified_number",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=13,
            sec_title="Общая площадь помещения",
            sec_name="total_square",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=14,
            sec_title="Жилая площадь",
            sec_name="residential_square",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=15,
            sec_title="Кол-во проживающих",
            sec_name="living_person_number",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=16,
            sec_title="Часовой пояс. Кол-во часов + или - от UTC",
            sec_name="timezone",
            sec_func="!timezone",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=17,
            sec_title="Альтернативный идентификатор ЛС, используется в некоторых конфигурациях.",
            sec_name="account_identifier",
            sec_func="spacerepl",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=18,
            sec_title="Признак нежилого помещения (0 1)",
            sec_name="not_residential",
            sec_is_service=False,
        )
        sec_number += 1
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=19,
            sec_title="Тип лицевого счета (uo|cr)",
            sec_name="account_type",
            sec_is_service=False,
        )
        sec_number += 1
        write_other_fields(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=20,
        )
    return file_name
