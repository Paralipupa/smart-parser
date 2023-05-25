from utils import get_ident, get_name, get_lines
from settings import *


def pp_charges(lines: list, path: str) -> str:
    names = []
    l = get_lines(lines)
    file_name = f"{path}/ini/4_pp_charges.ini"
    with open(file_name, "w") as file:
        file.write(
            ";########################################################################################################################\n"
        )
        file.write(
            ";-------------------------------------------------------------- pp_charges ----------------------------------------------\n"
        )
        file.write(
            ";########################################################################################################################\n"
        )
        file.write("[doc_2]\n")
        file.write("; Документ Начисления платежей\n")
        file.write("name=pp_charges\n")
        if lines["required"].get("required_pp_charges"):
            file.write(f'required_fields={",".join(lines["required"]["required_pp_charges"])}\n\n')
        else:
            file.write("required_fields=calc_value,recalculation\n\n")

        file.write("[pp_charges_0]\n")
        file.write("; ИНН, ОГРН или OrgID\n")
        file.write("name=org_ppa_guid\n")
        file.write("pattern=@\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        file.write("func=inn\n\n")

        file.write("[pp_charges_1]\n")
        file.write("; Внутренний идентификатор начисления\n")
        file.write("name=internal_id\n")
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        if lines["dic"].get("service"):
            file.write(
                f'offset_col_config={lines["dic"]["service"][0]["col"]}\n'
            )
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f"offset_pattern=@{name}\n")
            file.write(f"func=id+НЧ,spacerepl,hash\n\n")
        else:
            file.write(f"offset_col_config=0\n")
            file.write(f"offset_pattern=.+\n")
            file.write(
                f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+НЧ,spacerepl,hash\n\n'
            )
            for i, line in enumerate(l[1:]):
                file.write(f"[pp_charges_1_{i}]\n")
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f"offset_pattern=@{name}\n")
                file.write(
                    f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+НЧ,spacerepl,hash\n'
                )
            file.write("\n")

        file.write("[pp_charges_2]\n")
        file.write("; Внутренний идентификатор платежного документа\n")
        file.write("name=pp_internal_id\n")
        file.write("pattern=@0\n")
        file.write("row_data=0\n")
        if lines["dic"].get("pp_internal_id"):
            file.write(
                f'col_config={lines["dic"]["pp_internal_id"][0]["col"]}\n'
            )
        else:
            file.write("col_config=0\n")
        file.write("func=id+account_number,spacerepl,hash\n\n")

        names = []
        file.write("[pp_charges_3]\n")
        file.write("; Сумма начисления при однотарифном начислении\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=calc_value\n")
        if lines["dic"].get("service"):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f"pattern=@{name}\n")
            file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
            file.write(
                f'offset_col_config={lines["dic"]["calc_value"][0]["col"]}\n'
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
            file.write(f"[pp_charges_3_{i}]\n")
            file.write("; Сумма начисления при однотарифном начислении\n")
            file.write(f'; {line["name"].rstrip()}\n')
            if lines["dic"].get("service"):
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f"pattern=@{name}\n\n")
            else:
                file.write(f"offset_col_config={COLUMN_BEGIN+1+i}\n")
            file.write("\n")

        names = []
        file.write("[pp_charges_4]\n")
        file.write("; тариф при однотарифном начислении\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=tariff\n")
        if lines["dic"].get("service"):
            if lines["dic"].get("tariff"):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f"pattern=@{name}\n")
                file.write(
                    f'col_config={lines["dic"]["service"][0]["col"]}\n'
                )
                file.write(
                    f'offset_col_config={lines["dic"]["tariff"][0]["col"]}\n'
                )
                file.write("offset_pattern=.+\n\n")
                for i, line in enumerate(l[1:]):
                    file.write(f"[pp_charges_4_{i}]\n")
                    file.write("; тариф при однотарифном начислении\n")
                    file.write(f'; {line["name"].rstrip()}\n')
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f"pattern=@{name}\n")
                    file.write("\n")
        else:
            file.write("pattern=.+\n")
            file.write("col_config=0\n")
            file.write("row_data=0\n")
            file.write(
                f'func=key+fias+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash,dictionary\n\n'
            )
            for i, line in enumerate(l[1:]):
                file.write(f"[pp_charges_4_{i}]\n")
                file.write("; тариф при однотарифном начислении\n")
                file.write(f'; {line["name"].rstrip()}\n')
                file.write(
                    f'func=key+fias+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash,dictionary\n'
                )
                file.write("\n")

        names = []
        file.write("[pp_charges_5]\n")
        file.write("; Идентификатор услуги\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=service_internal_id\n")
        file.write("pattern=.+\n")
        file.write("row_data=0\n")

        if lines["dic"].get("service"):
            file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
            file.write(f"func=hash\n")
        else:
            file.write("col_config=0\n")
            file.write(
                f'func={l[0]["name"].split(";")[0].replace(","," ").replace("+","")},hash\n'
            )
        file.write("\n")

        if not lines["dic"].get("service"):
            for i, line in enumerate(l[1:]):
                file.write(f"[pp_charges_5_{i}]\n")
                file.write("; Идентификатор услуги\n")
                file.write(f'; {line["name"].rstrip()}\n')
                file.write(
                    f'func={line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()},hash\n'
                )
                file.write("\n")

        file.write("[pp_charges_6]\n")
        file.write("; кол-во услуги  при однотарифном начислении\n")
        file.write("name=rr\n\n")

        names = []
        file.write("[pp_charges_7]\n")
        file.write("; перерасчет\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=recalculation\n")
        if lines["dic"].get("service"):
            if lines["dic"].get("recalculation"):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f"pattern=@{name}\n")
                file.write(
                    f'col_config={lines["dic"]["service"][0]["col"]}\n'
                )
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

        names = []
        file.write("[pp_charges_8]\n")
        file.write("; Начислено за расчетный период,с  учетом перерасчета\n")
        file.write(f'; {l[0]["name"]}\n')
        file.write("name=accounting_period_total\n")
        if lines["dic"].get("service"):
            name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
            file.write(f"pattern=@{name}\n")
            file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
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
    return file_name
