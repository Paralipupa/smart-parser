from utils import get_lines
from sections import *


def pp_service(lines: list, path: str):
    l = get_lines(lines)
    doc_type = "pp_service"
    file_name = f'{path}/ini/5_pp_service.ini'
    with open(file_name, 'w') as file:
        write_section_caption(file, doc_type)
        write_section_doc(
            file, "doc", 3, "Документ. Услуги ", doc_type, required_fields="name")
        write_section_org_ppa_guid(file, lines, doc_type, 0,
                                   "ИНН, ОГРН или OrgID", "org_ppa_guid")
        write_section_internal_id(file, lines, doc_type, 1,
                                  "Внутренний идентификатор услуги", "internal_id")
        write_section_internal_id(file, lines, doc_type, 2,
                                  "наименование в 1с", "name", sec_is_hash=False)
        write_section_internal_id(file, lines, doc_type, 3,
                                  "вид в 1с (полное наименование)", "kind", sec_is_hash=False)
        write_section(file, lines, doc_type, 4, "код услуги в ГИС", "gis_code")

    return file_name
