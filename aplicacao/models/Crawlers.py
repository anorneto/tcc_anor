from typing import Dict
from requests_html import AsyncHTMLSession, HTMLSession, HTML, PyQuery
from abc import ABCMeta, abstractmethod

from .ResponseModels import ScrapResponse, AutoScrapResponse


class IBaseScrapper(metaclass=ABCMeta):
    # Constructor
    def __init__(self, config_name: str, url: str, selectors: Dict[str, str], render_page: bool = False,  is_async: bool = True):
        self.__config_name = config_name.strip()
        self.__url = url.strip()  # remove white spaces from string at beggining and end
        self.__selectors = selectors
        self.__is_async = is_async
        self.__render_page = render_page
        self.__html: HTML = None

        if is_async == True:
            self.__session = AsyncHTMLSession(verify=False)
        else:
            self.__session = HTMLSession(verify=False)

    @property
    def config_name(self):
        return self.__config_name

    @property
    def url(self):
        return self.__url

    @property
    def selectors(self):
        return self.__selectors

    @property
    def render_page(self):
        return self.__render_page

    @property
    def session(self):
        return self.__session

    @property
    def html(self):
        return self.__html or ''

    async def startSession(self):  # FIXME: transform this into a decorator??
        try:
            if self.__is_async:
                response = await self.__session.get(self.__url)
                if(self.__render_page == True):
                    await response.html.arender(timeout=120, sleep=5, wait=1)
                self.__html = response.html
            else:
                response = self.__session.get(self.__url)
                if(self.__render_page):
                    response.html.render(timeout=120, sleep=5, wait=1)
                self.__html = response.html
            return self.html
        except Exception as e:
            raise e

    @abstractmethod
    async def scrap(self):
        pass

    async def clearSession(self):
        if self.__is_async:
            await self.__session.close()
        else:
            self.__session.close()


class AsyncScrapper(IBaseScrapper):
    def __init__(self, config_name: str, url: str, selectors: Dict[str, str], render_page: bool = False, response_as_list: bool = False):
        super().__init__(config_name=config_name, url=url, selectors=selectors,
                         render_page=render_page, is_async=True)
        self.response_as_list = response_as_list

    async def scrap(self):
        try:
            await self.startSession()
            result = {
                "config_name": self.config_name,
                "url": self.url,
                "render_page": self.render_page
            }
            elements_found = dict()
            for key, value in self.selectors.items():
                elements_found[key] = self.html.find(value, clean=True)
            found_items = dict()
            max_length_elements_found = 0
            len_headers = len(elements_found)
            if len_headers:
                for key in elements_found:
                    elements_text = []
                    if(len(elements_found[key]) > max_length_elements_found):
                        max_length_elements_found = len(elements_found[key])
                    for element in elements_found[key]:
                        elements_text.append(
                            element.text.replace("\n", " ") if element.text else "")
                    found_items[key] = elements_text
                if(self.response_as_list):
                    headers = list(found_items.keys())
                    list_of_items = [
                        [""] * len_headers for i in range(max_length_elements_found)]
                    for index_header, value_header in enumerate(headers):
                        for index_item, value_item in enumerate(found_items[value_header]):
                            list_of_items[index_item][index_header] = value_item

                    result["headers"] = headers
                    result["items"] = list_of_items
                else:
                    result["items"] = found_items
                return result
            else:
                return "Nada Encontrado"
        except Exception as e:
            raise e
        finally:
            await self.clearSession()


class AutoScrapper(IBaseScrapper):
    def __init__(self, config_name: str, url: str, render_page: bool = False, strings: Dict[str, str] = []):
        super().__init__(config_name=config_name, url=url, selectors='',
                         render_page=render_page, is_async=True)
        self.strings = strings

    async def scrap(self):
        if not self.strings:
            return 'Nenhuma string definida para busca dos seletores'
        try:
            await self.startSession()
            result = result = {
                "config_name": self.config_name,
                "url": self.url,
                "render_page": self.render_page
            }
            wanted_selectors = dict()
            for string_key, string_value in self.strings.items():  # search for each string
                element_tree = self.html.find(
                    containing=string_value, clean=True)
                full_selector = ""
                last_selector = ""
                if isinstance(element_tree, list) and len(element_tree):
                    # If final element is a tr > td, lets find it index
                    index_element = None
                    if(element_tree[1].tag == "tr" and element_tree[0].tag == 'td'):
                        pyQuery = PyQuery(element_tree[1].html)

                        parent_element_children_text = []
                        for elem in pyQuery.items('td'):
                            parent_element_children_text.append(
                                elem.text() or "")

                        index_element = parent_element_children_text.index(
                            string_value) + 1
                    # reverse element order, so we can go from top element > final element
                    element_tree.reverse()
                    # searching for the element that contains the body
                    # and removing elements before the body tag
                    for element in element_tree:
                        if element.tag == "body":
                            body_index = element_tree.index(element)
                            # element_tree = element_tree[:body_index]
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
                            # if its a td, lets specufy the index of it
                            if(index_element is not None):
                                last_selector += f"table tbody tr {element.tag}:nth-of-type({index_element})"
                                full_selector += f":nth-of-type({index_element})"
                            elif(element_class != ""):
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
        except Exception as e:
            raise e
        finally:
            await self.clearSession()
