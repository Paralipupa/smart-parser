from sections import *


def accounts(lines: list, path: str) -> str:
    doc_type = "accounts"
    file_name = f'{path}/ini/2_accounts.ini'
    with open(file_name, 'w') as file:
        write_section_caption(file, doc_type)
        write_section_doc(
            file, "doc", 0, "Лицевые счета", doc_type, required_fields="address,account_number,living_person_number,total_square")
        write_section_org_ppa_guid(file, lines, doc_type, 0,
                                   "ИНН, ОГРН или OrgID", "org_ppa_guid")
        write_section(file, lines, doc_type, 1,
                      "Внутренний идентификатор договора", "contract_internal_id", sec_func="_+К,spacerepl,hash")
        write_section(file, lines, doc_type, 2,
                      "Внутренний идентификатор ЛС", "internal_id", sec_func="spacerepl,hash")
        write_section(file, lines, doc_type, 3,
                      "Идентификатор дома GUID", "fias", sec_func="!fias")
        write_section_address(file, lines, doc_type, 4,
                              "Адрес дома", "address")
        write_section(file, lines, doc_type, 5,
                      "Номер помещения (если есть)", "room_number")
        write_section(file, lines, doc_type, 6,
                      "ГИС. Идентификатор квартиры GUID", "gis_premises_id")
        write_section(file, lines, doc_type, 7,
                      "ГИС. Идентификатор блока GUID", "gis_block_id")
        write_section(file, lines, doc_type, 8,
                      "ГИС. Идентификатор комнаты GUID", "gis_room_id")
        write_section(file, lines, doc_type, 9,
                      "ГИС. Идентификатор ЛС GUID", "gis_account_id")
        write_section(file, lines, doc_type, 10, "Номер ЛС",
                      "account_number", sec_func="spacerepl")
        write_section(file, lines, doc_type, 11,
                      "ГИС. Идентификатор ЛС (20)", "gis_account_service_id")
        write_section(file, lines, doc_type, 12,
                      "ГИС. Номер ЛИ (20)", "gis_account_unified_number")
        write_section(file, lines, doc_type, 13,
                      "Общая площадь помещения", "total_square")
        write_section(file, lines, doc_type, 14,
                      "Жилая площадь", "residential_square")
        write_section(file, lines, doc_type, 15,
                      "Кол-во проживающих", "living_person_number")
        write_section(file, lines, doc_type, 16,
                      "Часовой пояс. Кол-во часов + или - от UTC", "timezone", sec_func="!timezone")
        write_section(file, lines, doc_type, 17,
                      "Альтернативный идентификатор ЛС, используется в некоторых конфигурациях.", "account_identifier", sec_func="spacerepl")
        write_section(file, lines, doc_type, 18,
                      "Признак нежилого помещения (0 1)", "not_residential")        
        write_section(file, lines, doc_type, 19,
                      "Тип лицевого счета (uo|cr)", "account_type")
    return file_name
