from typing import List
from requests_html import AsyncHTMLSession, HTMLSession, HTML
from abc import ABCMeta, abstractmethod


class IBaseScrapper(metaclass=ABCMeta):
    # Constructor
    def __init__(self, url: str, selectors: List[str], render_page: bool = False, is_async: bool = True):
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
    def __init__(self, url: str, selectors: List[str], render_page: bool = False):
        super().__init__(url=url, selectors=selectors,
                         render_page=render_page, is_async=True)

    async def scrap(self):
        try:
            await self.startSession()
            elements_found = {}
            for selector in self.selectors:
                elements_found[f"selector{self.selectors.index(selector)}"] = self.html.find(
                    selector)
            responseList = {}
            if len(elements_found):
                for key in elements_found:
                    elements_text = []
                    for element in elements_found[key]:
                        elements_text.append(element.text)
                    responseList[key] = elements_text
                return responseList
            else:
                return "Nada Encontrado"
        finally:
            await self.clearSession()


class AutoScrapper(IBaseScrapper):
    def __init__(self, url: str, render_page: bool = False, string_list: List[str] = []):
        super().__init__(url=url, selectors='',
                         render_page=render_page, is_async=True)
        self.string_list = string_list

    async def scrap(self):
        try:
            await self.startSession()
            wanted_selectors = []
            for wanted_string in self.string_list:  # search for each string

                element_tree = self.html.find(
                    containing=wanted_string)
                element_selector = ""
                if isinstance(element_tree, list) and len(element_tree):
                    # reverse element order, so we can go from top element > final element
                    element_tree.reverse()
                    # searching for the element that contains the body
                    # and removing elements before the body tag
                    for element in element_tree:
                        if element.tag == "body":
                            body_index = element_tree.index(element)
                            del element_tree[0:body_index]
                            break
                    for element in element_tree:
                        # add > before each tag after the first one
                        if len(element_selector) >= 1:
                            element_selector += ' > '
                        # populate selector for string
                        element_selector += f"{element.tag}"
                        # add class to the last element, the one that have the wanted string
                        if element_tree.index(element) == len(element_tree) - 1:
                            element_class = element.attrs.get("class") or ""
                            if(element_class != ""):
                                element_selector += f".{'.'.join(element_class) or ''}"
                    wanted_selectors.append(element_selector)
                else:
                    wanted_selectors.append(
                        f"Nada Encontrado para : {wanted_string}")
            return wanted_selectors
            # if isinstance(elements, list) and len(elements):
            #     for element in elements:
            #         responseList.append(element.text)
            #     return responseList
            # else:
            #     return "Nada Encontrado"
        finally:
            await self.clearSession()
