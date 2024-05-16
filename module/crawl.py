import certifi
from html.parser import HTMLParser
import csv
import requests

URL = "https://portal.eaeunion.org/sites/odata/_layouts/CDAC.Web/XmlSourceBrockerService.asmx/getViewXmlContentFriendly"
PARAMS_TEMPLATE = '<p>' \
                  '<parameter name="list" value="ec7f47f7-e8e6-48e1-9385-e75415c8211d"/>' \
                  '<parameter name="view" value="01d0337c-71f3-455b-950d-d882bf9547d9"/>' \
                  '<parameter name="itemUrl" value="/sites/odata/_layouts/15/Portal.EEC.Registry.UI/DisplayForm.aspx"/>' \
                  '<parameter name="orderbycolumn" value="OWSSCOPEDESCRIPTION"/>' \
                  '<parameter name="asc" value="false"/>' \
                  '<parameter name="query" value=""/>' \
                  '<parameter name="pagenumber" value="{}"/>' \
                  '</p>'
viewName = 'regui.SPLIST_TABLE_VIEW_S'
OUTPUT = "data.csv"

class EaeUnionParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.__next_page = None
        self.__data = []
        self.__item = {}
        self.__key = ''
        self.__work = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":  # ищем номер следующей страницы
            id = next((x for x in attrs if x[0] == 'id'), None)
            if id and id[1] == "PageLinkNext":
                params = next((x for x in attrs if x[0] == 'data-params'), None)
                if not params:
                    return
                params = params[1].split('&')
                for param in params:
                    parts = param.split('=')
                    if parts[0] == 'pagenumber':
                        self.__next_page = parts[1]
        if tag == "tbody":
            self.__work = True
        if self.__work and tag == "td":
            self.__key = next((x for x in attrs if x[0] == 'name'), "")[1]

    def handle_data(self, data):
        if self.__key != '':
            if self.__key in self.__item:
                self.__item[self.__key] += data
            else:
                self.__item[self.__key] = data

    def handle_endtag(self, tag):
        if tag == "td":
            self.__item[self.__key] = self.__item[self.__key].strip()
            self.__key = ''
        if self.__work and tag == "tr":
            self.__data.append(self.__item.copy())
            self.__item = {}
        if tag == "tbody":
            self.__work = False

    def get_next_page(self):
        return self.__next_page

    def get_data(self):
        return self.__data

    def feed(self, data):
        self.__next_page = None
        self.__data = []
        self.__item = {}
        self.__key = ''
        self.__work = False
        start = data.find('<![CDATA[')+len('<![CDATA[')
        end = data.find(']]>')
        super(EaeUnionParser, self).feed(data=data[start:end])


def main():
    page = 0
    parser = EaeUnionParser()
    while page is not None:
        resp = requests.post(url=URL, data={
            'viewName': viewName,
            'parameters': PARAMS_TEMPLATE.format(page)
        },verify=False)
        parser.feed(resp.content.decode('utf-8', 'ignore'))
        data = parser.get_data()
        if data:
            fieldnames = data[0].keys()
            method = 'w' if page == 0 else 'a'
            with open(OUTPUT, method, newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=";")
                if page == 0:
                    writer.writeheader()
                writer.writerows(data)
        print("page {} complete".format(page))
        page = parser.get_next_page()


if __name__ == "__main__":
    main()
