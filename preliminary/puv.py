from sections import *
from utils import get_ident, get_name, get_lines
from settings import *


def puv(lines: list, path: str) -> str:
    doc_type = "puv"
    file_name = f"{path}/ini/7_puv.ini"
    with open(file_name, "w") as file:
        write_section_caption(**dict(file=file, sec_type=doc_type))
        write_section_doc(
            **dict(
                file=file,
                sec_type="doc",
                sec_number=5,
                sec_title="ПУ показания",
                sec_name=doc_type,
                required_fields="rr1",
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
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=1,
                sec_title="Внутренний идентификатор ПУП",
                sec_name="internal_id",
                sec_suffix="ПУП",
                sec_is_service=True,
                sec_is_hash=True,
                sec_is_ident=True,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=2,
                sec_title="ГИС. Идентификатор ПУП GUID",
                sec_name="gis_id",
                sec_is_service=False,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=3,
                sec_title="Внутренний идентификатор ПУ",
                sec_name="metering_device_internal_id",
                sec_suffix="ПУ",
                sec_is_service=True,
                sec_is_hash=True,
                sec_is_ident=True,
            )
        )
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=4,
                sec_title="Дата",
                sec_name="date",
                sec_is_service=True,
                sec_is_hash=False,
                sec_is_ident=False,
            )
        )
        write_section_rr(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=5,
                sec_title="Показание 1",
                sec_name="rr1",
            )
        )
        write_section_rr(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=6,
                sec_title="Показание 2",
                sec_name="rr2",
            )
        )
        write_section_rr(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=7,
                sec_title="Показание 3",
                sec_name="rr3",
            )
        )

    return file_name
