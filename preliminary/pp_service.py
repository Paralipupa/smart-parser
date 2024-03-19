from utils import get_lines
from sections import *


def pp_service(lines: list, path: str):
    l = get_lines(lines)
    doc_type = "pp_service"
    file_name = f"{path}/ini/5_pp_service.ini"
    with open(file_name, "w") as file:
        write_section_caption(**dict(file=file, sec_type=doc_type))
        write_section_doc(
            **dict(
                file=file,
                sec_type="doc",
                sec_number=3,
                sec_title="Документ. Услуги ",
                sec_name=doc_type,
                required_fields="name",
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
        write_section_internal_id(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=1,
                sec_title="Внутренний идентификатор услуги",
                sec_name="internal_id",
                sec_is_service=True,
                sec_is_hash=True,
                sec_is_ident=False,
                sec_is_func_name=True,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=2,
                sec_title="наименование в 1с",
                sec_name="name",
                sec_is_service=True,
                sec_is_hash=False,
                sec_is_ident=False,
                sec_is_func_name=True,
            )
        )
        write_section_internal_id(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=3,
                sec_title="вид в 1с (полное наименование)",
                sec_name="kind",
                sec_is_service=True,
                sec_is_hash=False,
                sec_is_ident=False,
                sec_is_func_name=True,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=4,
                sec_title="код услуги в ГИС",
                sec_name="gis_code",
            )
        )

    return file_name
