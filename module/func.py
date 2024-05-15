import re, logging, datetime, uuid, os
from threading import Lock
from module.helpers import (
    hashit,
    get_index_find_any,
    get_index_key,
    get_value,
    regular_calc,
)
from module.settings import REG_KP_XLS, REG_ACCOUNT_NUMBER_BANK, REG_BIK_BANK

logger = logging.getLogger(__name__)


class Func:

    def __init__(self, parameters, dictionary, column_names, is_hash, parent):
        self.funcs = {
            "inn": self.func_inn,
            "period_first": self.func_period_first,
            "period_last": self.func_period_last,
            "period_month": self.func_period_month,
            "period_year": self.func_period_year,
            "column_name": self.func_column_name,
            "account_number": self.func_account_number,
            "bik": self.func_bik,
            "column_value": self.func_column_value,
            "hash": self.func_hash,
            "guid": self.func_uuid,
            "param": self.func_param,
            "spacerem": self.func_spacerem,
            "spacerepl": self.func_spacerepl,
            "round2": self.func_round2,
            "round4": self.func_round4,
            "round6": self.func_round6,
            "opposite": self.func_opposite,
            "param": self.func_param,
            "dictionary": self.func_dictionary,
            "dictionary_once": self.func_dictionaryOnce,
            "to_date": self.func_to_date,
            "id": self.func_id,
            "account_type": self.func_account_type,
            "fillzero9": self.func_fillzero9,
            "check_bank_accounts": self.func_bank_accounts,
            "cap_rep": self.func_cap_rep,
            "services": self.func_services,
            "source_file_name": self.func_source_file_name,
        }
        self._current_value = list()
        self._current_id = ""
        self._parameters = parameters
        self._dictionary = dictionary
        self._column_names = column_names
        self.is_hash = is_hash
        self.parent = parent
        self.lock = Lock()

    def __get_func_list(self, part: str, names: str):
        self._current_value_func.setdefault(part, {})
        list_sub = re.findall(r"[a-z_0-9]+\(.+?\)", names)
        for item in list_sub:
            ind_s = item.find("(")
            ind_e = item.find(")")
            func = item[:ind_s]
            arg = item[ind_s + 1 : ind_e]
            hash = hashit(func.encode("utf-8"))[:8]
            if not self._current_value_func[part].get(hash):
                self._current_value_func[part][hash] = {
                    "name": func,
                    "type": "sub",
                    "input": "",
                    "output": "",
                }
                arg_hash = self.__get_func_list(hash, arg)
                self._current_value_func[hash]["expression"] = arg_hash
                names = names.replace(item, hash)
        names_new = ""
        while True:
            index = get_index_find_any(names, "+-,")
            delim = ""
            if index == -1:
                item = names
                names = ""
            else:
                item = names[:index]
                delim = names[index : index + 1]
                names = names[index + 1 :]
            hash = hashit(item.encode("utf-8"))[:8]
            self._current_value_func[part][hash] = {
                "name": item,
                "type": "",
                "input": "",
                "output": "",
            }
            names_new += f"{hash}{delim}"
            if not names:
                break
        return names_new

    def __recalc_expression(self, part: str) -> None:
        for item in self._current_value_func[part]["expression"].split(","):
            value = self._current_value_empty
            for index, hash in enumerate(re.split(r"[+-]", item)):
                self._current_index = 0
                name = self._current_value_func[part][hash]["name"]
                if regular_calc(r"(?<=\[)\d(?=\])", name):
                    # индекс значения словаря определен в квадратных скобках
                    self._current_index = int(re.findall(r"(?<=\[)\d(?=\])", name)[0])
                    name = re.findall(r".+(?=\[)", name)[0]
                if self._current_value_func[part].get(name):
                    self._current_value.append(value)
                    ind = self._current_index
                    self.__recalc_expression(name)
                    self._current_index = ind
                    name = self._current_value_func[part][name]["name"]
                if self.funcs.get(name.strip()):
                    f = self.funcs.get(name.strip())
                    x = f()
                    if isinstance(value, float) or isinstance(value, int):
                        if item.find(f"-{name}") != -1 and index != 0:
                            value -= get_value(x, ".+", "float")
                        else:
                            value += get_value(x, ".+", "float")
                    else:
                        value += x + " "
                else:
                    if self._dictionary.get(get_index_key(name)):
                        value = value.strip() + self.func_dictionary(name)
                    elif self._parameters.get(name):
                        value = value.strip() + (
                            self._parameters[name]["value"][-1]
                            if len(self._parameters[name]["value"]) > 0
                            else ""
                        )
                    elif name == "_":
                        value = (
                            value.strip()
                            + (" " if value else "")
                            + self._current_value[-1]
                        )
                    else:
                        if isinstance(value, str):
                            value = value.strip() + (" " if value else "") + name
                        else:
                            pass
                if self._current_value_func[part].get(
                    self._current_value_func[part][hash]["name"]
                ):
                    self._current_value.pop()
            self._current_value.pop()
            self._current_value.append(
                value.rstrip() if isinstance(value, str) else value
            )

    def func(
        self, team: dict = {}, fld_param: dict = {}, row: int = 0, col: int = 0
    ) -> str:
        # self.lock.acquire()
        try:
            self._current_id = fld_param.get("value", "")
            self._current_index = 0
            self._current_value = list()
            if fld_param.get("is_offset"):
                value = fld_param.get("value_o", "")
                self._current_value_type = fld_param.get("offset_type", "str")
            else:
                value = fld_param.get("value", "")
                self._current_value_type = fld_param.get("type", "str")
            if bool(value) is False and not fld_param.get("func_is_empty", True):
                return ""
            if fld_param.get("func_pattern") and fld_param.get("func_pattern")[0]:
                self._current_value_pattern = fld_param["func_pattern"][0]
            else:
                if fld_param.get("is_offset"):
                    self._current_value_pattern = (
                        fld_param["offset_pattern"][0]
                        if fld_param.get("offset_pattern")
                        and fld_param["offset_pattern"][0]
                        else ".+"
                    )
                else:
                    self._current_value_pattern = (
                        fld_param["pattern"][0]
                        if fld_param.get("pattern") and fld_param["pattern"][0]
                        else ".+"
                    )
            self._current_value_empty = (
                0
                if self._current_value_type == "float"
                and not "dictionary" in fld_param.get("func", "")
                else ""
            )
            self._current_value_team = team
            self._current_value_row = (
                row if not "dictionary" in fld_param.get("func", "") else 0
            )
            self._current_value_col = col
            self._current_value_param = fld_param
            self._current_value_func_is_no_return = fld_param.get(
                "func_is_no_return", False
            )
            self._current_value_func = {}
            part = "00000000"
            m = fld_param.get("func", "")
            m = self.__get_func_list(part, m)
            self._current_value_func[part]["expression"] = m
            self._current_value.append(value)
            try:
                self.__recalc_expression(part)
                value = self._current_value.pop()
            except Exception as ex:
                logger.exception(f"Func:{ex}")
                value = ""
            if self._current_value_func_is_no_return and str(value).strip():
                for x in [
                    x
                    for x in re.split(r"[+-,]", fld_param.get("func", ""))
                    if regular_calc("^[a-z_0-9]+$", x)
                ]:
                    if str(value).find(x) != -1:
                        value = ""
                        break
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            # self.lock.release()
            pass
        return str(value).strip()

    def func_inn(self):
        if self._parameters["inn"]["value"][0] != "0000000000":
            return self._parameters["inn"]["value"][0].split("|")[-1]
        else:
            return self._parameters["inn"]["value"][-1].split("|")[-1]

    def func_period_first(self):
        period = datetime.datetime.strptime(
            self._parameters["period"]["value"][-1], "%d.%m.%Y"
        )
        return period.replace(day=1).strftime("%d.%m.%Y")

    def func_period_last(self):
        period = datetime.datetime.strptime(
            self._parameters["period"]["value"][-1], "%d.%m.%Y"
        )
        next_month = period.replace(day=28) + datetime.timedelta(days=4)
        return (next_month - datetime.timedelta(days=next_month.day)).strftime(
            "%d.%m.%Y"
        )

    def func_period_month(self):
        return self._parameters["period"]["value"][0][3:5]

    def func_period_year(self):
        return self._parameters["period"]["value"][0][6:]

    def func_to_date(self):
        patts = [
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%y",
            "%d.%m.%y",
            "%d/%m/%y",
            "%B %Y",
        ]
        for p in patts:
            try:
                d = datetime.datetime.strptime(self._current_value[-1], p)
                return self._current_value[-1]
            except:
                pass
        return ""

    def func_hash(self):
        return (
            hashit(str(get_index_key(self._current_value[-1])).encode("utf-8"))
            if self.is_hash and self._current_value[-1]
            else self._current_value[-1]
        )

    def func_uuid(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self._current_value[-1]))

    def func_id(self, current_id=None):
        d = self._parameters["period"]["value"][0]
        id = str(self._current_id).strip() if current_id is None else current_id
        if id and self._parameters.get("id_length") is not None:
            id = id.rjust(int(self._parameters["id_length"]["value"][0]), "0")
        return f"{id}_{d[3:5]}{d[6:]}"  # _mmyyyy

    def func_column_name(self):
        if self._current_value_col != -1:
            return self.__get_columns_heading(self._current_value_, "alias")
        return ""

    def func_column_value(self):
        try:
            value = next(
                (
                    x[self._current_value_row]["value"]
                    for x in self._current_value_team.values()
                    if len(x) > self._current_value_row
                    and x[self._current_value_row]["col"]
                    == int(self._current_value[-1])
                ),
                "",
            )
            return value.strip() if isinstance(value, str) else value
        except Exception as ex:
            logger.error(f"{ex}")
        return ""

    def func_param(self):
        m = ""
        for item in self._parameters[self._current_value[-1]]["value"]:
            m += (item.strip() + " ") if isinstance(item, str) else ""
        return f"{m.strip()}"

    def func_spacerem(self):
        return self._current_value[-1].strip().replace(" ", "")

    def func_spacerepl(self):
        return self._current_value[-1].strip().replace(" ", "_")

    def func_round2(self):
        return (
            str(round(self._current_value[-1], 2))
            if isinstance(self._current_value[-1], float)
            else str(self._current_value[-1])
        )

    def func_round4(self):
        return (
            str(round(self._current_value[-1], 4))
            if isinstance(self._current_value[-1], float)
            else self._current_value[-1]
        )

    def func_round6(self):
        return (
            str(round(self._current_value[-1], 6))
            if isinstance(self._current_value[-1], float)
            else self._current_value[-1]
        )

    def func_opposite(self):
        return (
            str(-self._current_value)
            if isinstance(self._current_value, float)
            else self._current_value
        )

    def func_account_number(self):
        pattern: re.compile = re.compile(REG_KP_XLS, re.IGNORECASE)
        parrent_account: re.compile = re.compile(REG_ACCOUNT_NUMBER_BANK, re.IGNORECASE)
        if self._dictionary.get("account_number"):
            if pattern.search(
                self._parameters["filename"]["value"][0].lower(), re.IGNORECASE
            ):
                return (
                    self._dictionary.get("account_number", [])[-1]["value"]
                    if len(self._dictionary.get("account_number", [])) != 0
                    and parrent_account.search(
                        self._dictionary.get("account_number", [])[-1]["value"]
                    )
                    else ""
                )
            else:
                return (
                    self._dictionary.get("account_number", [])[0]["value"]
                    if len(self._dictionary.get("account_number", [])) != 0
                    and parrent_account.search(
                        self._dictionary.get("account_number", [])[-1]["value"]
                    )
                    else ""
                )
        elif self._parameters.get("account_number"):
            if pattern.search(
                self._parameters["filename"]["value"][0].lower(), re.IGNORECASE
            ):
                return (
                    self._parameters.get("account_number", {"value": [""]})["value"][-1]
                    if len(
                        self._parameters.get("account_number", {"value": [""]})["value"]
                    )
                    != 0
                    and parrent_account.search(
                        self._parameters.get("account_number", {"value": [""]})[
                            "value"
                        ][-1]
                    )
                    else ""
                )
            else:
                return (
                    self._parameters.get("account_number", {"value": [""]})["value"][0]
                    if len(
                        self._parameters.get("account_number", {"value": [""]})["value"]
                    )
                    != 0
                    and parrent_account.search(
                        self._parameters.get("account_number", {"value": [""]})[
                            "value"
                        ][0]
                    )
                    else ""
                )
        else:
            return ""

    def func_bik(self):
        pattern = re.compile(REG_KP_XLS, re.IGNORECASE)
        if self._dictionary.get("bik"):
            if pattern.search(self._parameters["filename"]["value"][0].lower()):
                return (
                    self._dictionary.get("bik", [])[-1]["value"]
                    if len(self._dictionary.get("bik", [])) != 0
                    else ""
                )
            else:
                return (
                    self._dictionary.get("bik", [])[0]["value"]
                    if len(self._dictionary.get("bik", [])) != 0
                    else ""
                )
        elif self._parameters.get("bik"):
            if pattern.search(self._parameters["filename"]["value"][0].lower()):
                return (
                    self._parameters.get("bik", {"value": [""]})["value"][-1]
                    if len(self._parameters.get("bik", {"value": [""]})["value"]) != 0
                    else ""
                )
            else:
                return (
                    self._parameters.get("bik", {"value": [""]})["value"][0]
                    if len(self._parameters.get("bik", {"value": [""]})["value"]) != 0
                    else ""
                )
        else:
            return ""

    def func_dictionary(self, key: str = None):
        return self.__func_dictionary(key, False)

    def func_dictionaryOnce(self, key: str = None):
        """Берет значение словаря только один раз
        Повторный вызов с этим ключом игнорируется
        """
        return self.__func_dictionary(key, True)

    def __func_dictionary(self, key: str = None, is_not_used: bool = False):
        name = get_index_key(self._current_value[-1] if key is None else key)
        dictionary = self._dictionary.get(name, [])
        value = ""
        if len(dictionary) > self._current_index:
            if is_not_used is False or dictionary[self._current_index]["used"] is False:
                value = dictionary[self._current_index]["value"]
                dictionary[self._current_index]["used"] = True
        elif len(dictionary) > 0:
            if is_not_used is False or dictionary[-1]["used"] is False:
                value = dictionary[-1]["value"]
                dictionary[self._current_index]["used"] = True

        if len(dictionary) > 1 and not re.search(self._current_value_pattern, value):
            for val in dictionary:
                if (is_not_used is False or val["used"] is False) and re.search(
                    self._current_value_pattern, val["value"]
                ):
                    val["used"] = True
                    return val["value"]
        return value

    def func_account_type(self):
        is_cap = False
        comp: re.compile = re.compile(REG_KP_XLS, re.IGNORECASE)
        for key in self._column_names.keys():
            if comp.search(key):
                is_cap = True
                break
        if is_cap or comp.search(self._parameters["filename"]["value"][0].lower()):
            return "cr"
        else:
            return ""

    def func_fillzero9(self):
        return str(self._current_value[-1]).strip().rjust(9, "0") + " "

    def func_bank_accounts(self):
        if not self._current_value_team:
            return ""
        d = {}
        u = {}
        exist_overhaul = False
        for item in self._current_value_team["noname"]:
            d.setdefault(item.get("internal_id"), item)
        for item in d.values():
            if item.get("is_overhaul"):
                exist_overhaul = True
            u.setdefault(item["account_number"], 0)
            u[item["account_number"]] += 1
        if exist_overhaul == False:
            if self.parent:
                mess = 'В тарифах отсутствует колонка "Кап.ремонт"'
                self.parent.add_warning(mess)
        if [x for x in u.values() if x > 1]:
            if self.parent:
                mess = "Конфликт в расчетном счете по капитальному ремонту"
                self.parent.add_warning(mess)
        return ""

    def func_cap_rep(self):
        return "1" if str(self._current_value[-1]).strip() == "cr" else ""

    def func_services(self):
        return ""

    def func_source_file_name(self):
        try:
            return os.path.basename(self._parameters['filename']['value'][0])
        except Exception as ex:
            return f"{ex}"
