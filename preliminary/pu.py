from sections import *

def pu(lines: list, path: str) -> str:
    doc_type = "pu"
    file_name = f'{path}/ini/6_pu.ini'
    with open(file_name, 'w') as file:
        write_section_caption(file, doc_type)
        write_section_doc(
            file, "doc", 4, "Приборы учета (ПУ)", doc_type, "internal_id")
        write_section_org_ppa_guid(file, lines, doc_type, 0,
                                   "ИНН, ОГРН или OrgID", "org_ppa_guid")
        write_section_internal_id(file, lines, doc_type, 1,
                                  "Внутренний идентификатор ПУ", "internal_id", "ПУ")
        write_section_account_internal_id(file, lines, doc_type, 2,
                                          "Внутренний идентификатор ЛС", "account_internal_id")
        write_section(file, lines, doc_type, 3,
                      "ГИС. Идентификатор ПУ GUID", "gis_id")
        write_section(file, lines, doc_type, 4, "Серийный номер", "serial_number")
        write_section(file, lines, doc_type, 5, "Тип устройства", "device_type")
        write_section(file, lines, doc_type, 6, "Производитель", "manufacturer")
        write_section(file, lines, doc_type, 7, "Модель", "model")
        write_section(file, lines, doc_type, 8,
                      "Показания момент установки. Тариф 1", "rr1", "_pu")
        write_section(file, lines, doc_type, 9,
                      "Показания момент установки. Тариф 2", "rr2")
        write_section(file, lines, doc_type, 10,
                      "Показания момент установки. Тариф 3", "rr3")
        write_section(file, lines, doc_type, 11,
                      "Дата установки", "installation_date")
        write_section(file, lines, doc_type, 12,
                      "Дата начала работы", "commissioning_date")
        write_section(file, lines, doc_type, 13,
                      "Дата следующей поверки", "next_verification_date")
        write_section(file, lines, doc_type, 14,
                      "Дата последней поверки", "first_verification_date")
        write_section(file, lines, doc_type, 15,
                      "Дата опломбирования", "factory_seal_date")
        write_section(file, lines, doc_type, 16,
                      "Интервал проверки (кол-во месяцев)", "checking_interval")
        write_section_service_internal_id(file, lines, doc_type, 17,
                                          "Идентификатор услуги", "service_internal_id")
    return file_name
