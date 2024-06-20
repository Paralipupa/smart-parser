from utils import get_ident, get_name, get_lines, get_func_name
from sections import *
from settings import *


def pp_charges(lines: list, path: str, sec_number: int) -> str:
    names = []
    l = get_lines(lines)
    file_name = f"{path}/ini/4_pp_charges.ini"
    with open(file_name, "w") as file:
        doc_type = "pp_charges"
        required_fields = (
            ",".join(lines["required"]["required_pp_charges"])
            if lines["required"].get("required_pp_charges")
            else "calc_value,recalculation"
        )
        write_section_caption(**dict(file=file, sec_type=doc_type))
        write_section_doc(
            **dict(
                file=file,
                lines=lines,
                sec_type="doc",
                sec_number=sec_number,
                sec_title="Документ Начисления платежей",
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
                sec_number=0,
                sec_title="ИНН, ОГРН или OrgID",
                sec_name="org_ppa_guid",
            )
        )
        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=1,
                sec_title="Внутренний идентификатор начисления",
                sec_name="internal_id",
                sec_suffix="НЧ",
                sec_is_service=True,
                sec_is_hash=True,
                sec_is_ident=True,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=2,
                sec_title="Внутренний идентификатор платежного документа",
                sec_name="pp_internal_id",
                sec_is_service=False,
                sec_is_hash=True,
                sec_is_ident=True,
                sec_is_func_name_no_ident=False,
                sec_func="id+account_number,spacerepl,hash",
            )
        )

        sec_number += 1
        names = []
        file.write("\n")
        file.write("[pp_charges_3]\n")
        file.write("; Сумма начисления при однотарифном начислении\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=calc_value\n")
        if lines["dic"].get("service"):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f"pattern=@{name}\n")
            file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
            if lines["dic"].get("calc_value"):
                file.write(
                    f'offset_col_config={lines["dic"]["calc_value"][0]["col"]}\n'
                )
            else:
                if lines["dic"].get("bill_value"):
                    file.write(
                        f'offset_col_config={lines["dic"]["bill_value"][0]["col"]}\n'
                    )
                else:
                    file.write(f"offset_col_config=2\n")
        else:
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write(f"offset_col_config={COLUMN_BEGIN}\n")
        file.write("offset_pattern=@currency\n")
        file.write("offset_type=float\n")
        file.write("func=round2\n")
        file.write("\n")
        for i, line in enumerate(l[1:]):
            file.write(f"[pp_charges_3_{i}]\n")
            file.write("; Сумма начисления при однотарифном начислении\n")
            file.write(f'; {line["name"].rstrip()}\n')
            if lines["dic"].get("service"):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f"pattern=@{name}\n\n")
            else:
                file.write(f"offset_col_config={COLUMN_BEGIN+1+i}\n")
            file.write("\n")

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=4,
                sec_title="тариф при однотарифном начислении",
                sec_name="tariff",
                sec_is_service=True,
                sec_is_hash=True,
                sec_is_ident=True if not lines["dic"].get("service") else False,
                sec_is_func_name=True if not lines["dic"].get("service") else False,
                sec_func_ident="key+fias",
                sec_func_pattern="[0-9-]+(?:[.,][0-9]*)?",
                sec_is_func_dictionary=True,
            )
        )

        sec_number += 1
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="Идентификатор услуги",
                sec_name="service_internal_id",
                sec_is_service=True,
                sec_is_hash=True,
                sec_is_ident=False,
                sec_is_func_name=True,
                sec_is_func_name_no_ident=False,
                required_fields=required_fields,
            )
        )

        sec_number += 1
        # file.write("\n")
        # file.write("[pp_charges_6]\n")
        # file.write("; кол-во услуги  при однотарифном начислении\n")
        # file.write("name=rr\n")
        write_section(
            **dict(
                file=file,
                lines=lines,
                sec_type=doc_type,
                sec_number=sec_number,
                sec_title="кол-во услуги  при однотарифном начислении",
                sec_name="rr",
                # sec_is_service=True,
                # sec_is_hash=False,
                # sec_is_ident=False,
                # sec_is_func_name=False,
                # sec_is_func_name_no_ident=False,
                required_fields=required_fields,
            )
        )

        sec_number += 1
        names = []
        file.write("\n")
        file.write("[pp_charges_7]\n")
        file.write("; перерасчет\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=recalculation\n")
        if lines["dic"].get("service"):
            if lines["dic"].get("recalculation"):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f"pattern=@{name}\n")
                file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
                if lines["dic"]["recalculation"][0]["offset"]:
                    file.write(
                        f'offset_col_config={lines["dic"]["recalculation"][0]["offset"][0]}\n'
                    )
                else:
                    file.write(
                        f'offset_col_config={lines["dic"]["recalculation"][0]["col"]}\n'
                    )
                file.write("offset_pattern=@currency\n")
                file.write("offset_type=float\n")
                file.write("func=round2\n")
                file.write("\n")
                for i, line in enumerate(l[1:]):
                    file.write(f"[pp_charges_7_{i}]\n")
                    file.write("; перерасчет\n")
                    file.write(f'; {line["name"].rstrip()}\n')
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f"pattern=@{name}\n")
                    file.write("\n")
        else:
            file.write("\n")

        sec_number += 1
        names = []
        file.write("\n")
        file.write("[pp_charges_8]\n")
        file.write("; Начислено за расчетный период,с  учетом перерасчета\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=accounting_period_total\n")
        if lines["dic"].get("service"):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f"pattern=@{name}\n")
            file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
            if lines["dic"]["accounting_period_total"][0]["offset"]:
                file.write(
                    f'offset_col_config={lines["dic"]["accounting_period_total"][0]["offset"][0]}\n'
                )
            else:
                file.write(
                    f'offset_col_config={lines["dic"]["accounting_period_total"][0]["col"]}\n'
                )
        else:
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write(f"offset_col_config={COLUMN_BEGIN}\n")
        file.write("offset_pattern=@currency\n")
        file.write("offset_type=float\n")
        file.write("func=round2\n")
        file.write("\n")
        for i, line in enumerate(l[1:]):
            file.write(f"[pp_charges_8_{i}]\n")
            file.write("; Сумма начисления при однотарифном начислении\n")
            file.write(f'; {line["name"].rstrip()}\n')
            if lines["dic"].get("service"):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f"pattern=@{name}\n")
            else:
                file.write(f"offset_col_config={COLUMN_BEGIN+1+i}\n")
            file.write("\n")

        sec_number += 1
        write_other_fields(
            file=file,
            lines=lines,
            sec_type=doc_type,
            sec_number=sec_number,
        )
    return file_name
