import asyncio
from requests_html import AsyncHTMLSession, HTMLSession, HTML
from abc import ABCMeta, abstractmethod


class IBaseScrapper(metaclass=ABCMeta):
    # Constructor
    def __init__(self, url: str, selectors: str, render_page: bool = False, is_async: bool = True):
        self.__url = url
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
    def __init__(self, url: str, selectors: str, render_page: bool = False):
        super().__init__(url=url, selectors=selectors,
                         render_page=render_page, is_async=True)

    async def scrap(self):
        try:
            await self.startSession()
            elements = self.html.find(self.selectors)
            responseList = []
            if isinstance(elements, list) and len(elements):
                for element in elements:
                    responseList.append(element.text)
                return responseList
            else:
                return "Nada Encontrado"
        finally:
            await self.clearSession()
