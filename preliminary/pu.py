from sections import *


def pu(lines: list, path: str) -> str:
    doc_type = "pu"
    file_name = f"{path}/ini/6_pu.ini"
    with open(file_name, "w") as file:
        required_fields = (
            ",".join(lines["required"]["required_pu"])
            if lines["required"].get("required_pu")
            else "serial_number,manufacturer,model"
        )
        write_section_caption(file, doc_type)
        write_section_doc(
            file,
            "doc",
            4,
            "Приборы учета (ПУ)",
            doc_type,
            required_fields=required_fields,
        )
        write_section_org_ppa_guid(
            file, lines, doc_type, 0, "ИНН, ОГРН или OrgID", "org_ppa_guid"
        )
        write_section_internal_id(
            file, lines, doc_type, 1, "Внутренний идентификатор ПУ", "internal_id", "ПУ"
        )
        write_section_account_internal_id(
            file,
            lines,
            doc_type,
            2,
            "Внутренний идентификатор ЛС",
            "account_internal_id",
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=3,
            sec_title="ГИС. Идентификатор ПУ GUID",
            sec_name="gis_id",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=4,
            sec_title="Серийный номер",
            sec_name="serial_number",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=5,
            sec_title="Тип устройства",
            sec_name="device_type",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=6,
            sec_title="Производитель",
            sec_name="manufacturer",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=7,
            sec_title="Модель",
            sec_name="model",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=8,
            sec_title="Показания момент установки. Тариф 1",
            sec_name="rr1",
            sec_prefix="_pu",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=9,
            sec_title="Показания момент установки. Тариф 2",
            sec_name="rr2",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=10,
            sec_title="Показания момент установки. Тариф 3",
            sec_name="rr3",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=11,
            sec_title="Дата установки",
            sec_name="installation_date",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=12,
            sec_title="Дата начала работы",
            sec_name="commissioning_date",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=13,
            sec_title="Дата следующей поверки",
            sec_name="next_verification_date",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=14,
            sec_title="Дата последней поверки",
            sec_name="first_verification_date",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=15,
            sec_title="Дата опломбирования",
            sec_name="factory_seal_date",
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=16,
            sec_title="Интервал проверки (кол-во месяцев)",
            sec_name="checking_interval",
            required_fields=required_fields,
        )
        write_section_service_internal_id(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=17,
            sec_title="Идентификатор услуги",
            sec_name="service_internal_id",
            required_fields=required_fields,
        )
        write_section(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=18,
            sec_title="Тип лицевого счета (uo|cr)",
            sec_name="account_type",
            required_fields=required_fields,
        )
    return file_name
