from typing import Dict
from lxml.html import clean
from requests_html import AsyncHTMLSession, HTMLSession, HTML
from abc import ABCMeta, abstractmethod


class IBaseScrapper(metaclass=ABCMeta):
    # Constructor
    def __init__(self, url: str, selectors: Dict[str, str], render_page: bool = False, is_async: bool = True):
        self.__url = url.strip()  # remove white spcaes from string at beggining and end
        self.__selectors = selectors
        self.__is_async = is_async
        self.__render_page = render_page
        self.__session = AsyncHTMLSession() if is_async == True else HTMLSession()
        self.__html: HTML = None

    @property
    def url(self):
        return self.__url

    @property
    def selectors(self):
        return self.__selectors

    @property
    def session(self):
        return self.__session

    @property
    def html(self):
        return self.__html or ''

    async def startSession(self):  # FIXME: transform this into a decorator??
        if self.__is_async:
            response = await self.__session.get(self.__url)
            if(self.__render_page == True):
                await response.html.arender(timeout=30, sleep=10,)
            self.__html = response.html
        else:
            response = self.__session.get(self.__url)
            if(self.__render_page):
                response.html.render(timeout=30, sleep=10,)
            self.__html = response.html
        return self.html

    @abstractmethod
    async def scrap(self):
        pass

    async def clearSession(self):
        if self.__is_async:
            await self.__session.close()
        else:
            self.__session.close()


class AsyncScrapper(IBaseScrapper):
    def __init__(self, url: str, selectors: Dict[str, str], render_page: bool = False):
        super().__init__(url=url, selectors=selectors,
                         render_page=render_page, is_async=True)

    async def scrap(self):
        try:
            await self.startSession()
            result = {"url": self.url}
            elements_found = {}
            for key, value in self.selectors.items():
                elements_found[key] = self.html.find(value, clean=True)
            found_itens = {}
            if len(elements_found):
                for key in elements_found:
                    elements_text = []
                    for element in elements_found[key]:
                        elements_text.append(
                            element.text if element.text else "Nada encontrado")
                    found_itens[key] = elements_text

                result["itens"] = found_itens
                return result
            else:
                return "Nada Encontrado"
        finally:
            await self.clearSession()


class AutoScrapper(IBaseScrapper):
    def __init__(self, config_name: str, url: str, render_page: bool = False, strings: Dict[str, str] = []):
        super().__init__(url=url, selectors='',
                         render_page=render_page, is_async=True)
        self.strings = strings
        self.render_page = render_page
        self.config_name = config_name

    async def scrap(self):
        if not self.strings:
            return 'Nenhuma string definida para busca dos seletores'
        try:
            await self.startSession()
            result = {"config_name": self.config_name,
                      "render_page": self.render_page}
            wanted_selectors = dict()
            for string_key, string_value in self.strings.items():  # search for each string
                element_tree = self.html.find(
                    containing=string_value, clean=True)
                full_selector = ""
                last_selector = ""
                if isinstance(element_tree, list) and len(element_tree):
                    # reverse element order, so we can go from top element > final element
                    element_tree.reverse()
                    # searching for the element that contains the body
                    # and removing elements before the body tag
                    for element in element_tree:
                        if element.tag == "body":
                            body_index = element_tree.index(element)
                            #element_tree = element_tree[:body_index]
                            del element_tree[0:body_index]
                            break
                    for element in element_tree:
                        # add > before each tag after the first one
                        if len(full_selector) >= 1:
                            full_selector += ' > '
                        # populate selector for string
                        full_selector += f"{element.tag}"
                        # add class to the last element, the one that have the wanted string
                        if element_tree.index(element) == len(element_tree) - 1 or element.text == string_value:
                            element_class = element.attrs.get("class") or ""
                            if(element_class != ""):
                                last_selector = f"{(element.tag) +'.'+'.'.join(element_class)}"
                                full_selector += f".{'.'.join(element_class) or ''}"
                        if element.text == string_value:
                            break
                    wanted_selectors[string_key] = {
                        "full": full_selector, "last": last_selector}
                else:
                    wanted_selectors[string_key] = {"full": "", "last": ""}
                result["selectors"] = wanted_selectors
            return result
        finally:
            await self.clearSession()
