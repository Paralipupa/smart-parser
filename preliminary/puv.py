from sections import *
from utils import get_ident, get_name, get_lines
from settings import *


def puv(lines: list, path: str) -> str:
    doc_type = "puv"
    file_name = f'{path}/ini/7_puv.ini'
    with open(file_name, 'w') as file:
        write_section_caption(file, doc_type)
        write_section_doc(
            file, "doc", 5, "ПУ показания", doc_type, required_fields="rr1")

        write_section_org_ppa_guid(file, lines, doc_type, 0,
                                   "ИНН, ОГРН или OrgID", "org_ppa_guid")
        write_section_internal_id(file, lines, doc_type, 1,
                                  "Внутренний идентификатор ПУП", "internal_id", "ПУП")
        write_section(file, lines, doc_type, 2,
                      "ГИС. Идентификатор ПУП GUID", "gis_id")
        write_section_internal_id(file, lines, doc_type, 3,
                                  "Внутренний идентификатор ПУ", "metering_device_internal_id", "ПУ")
        write_section(file, lines, doc_type, 4, "Дата", "date")
        write_section_rr(file, lines, doc_type, 5, "Показание 1", "rr1")
        write_section_rr(file, lines, doc_type, 6, "Показание 2", "rr2")
        write_section_rr(file, lines, doc_type, 7, "Показание 3", "rr3")

    return file_name
