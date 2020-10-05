import asyncio
import json
from requests_html import AsyncHTMLSession


class ScrapTest:

    def __init__(self, url_to_scrap: str, selectors: str, should_print: int, should_render: int):
        self.url_to_scrap = url_to_scrap
        self.selectors = selectors
        self.should_print = should_print
        self.should_render = should_render

    async def scrap(self):
        asession = AsyncHTMLSession()
        response = await asession.get(self.url_to_scrap)
        if self.should_render == 1:
            await response.html.arender(timeout=30, sleep=10, keep_page=True)
            await response.html.page.screenshot(path='example.png')
            await response.html.page.pdf(path='example.pdf', fullPage=True)

        elements = response.html.find(self.selectors)
        if len(elements):
            if self.should_print == 1:
                for element in elements:
                    print(element.text)
            else:
                with open('teste.json', 'w', encoding='utf8') as outfile:
                    json.dump(obj=list(map(lambda x: x.text, elements)),  # lambda transforma element em list[string]
                              fp=outfile, ensure_ascii=False)
        else:
            print("Nada Encontrado")
        await asession.close()


async def main():
    while True:
        url_to_scrap = input("Entre o Site para fazer scrapping:")
        if url_to_scrap == "teste":
            task1 = asyncio.create_task(
                ScrapTest('https://hardmob.com.br/promocoes/', 'h3.threadtitle', 1, 0).scrap())
            task2 = asyncio.create_task(
                ScrapTest("https://consultas.anvisa.gov.br/#/medicamentos/2500100649273/?nomeProduto=Paracetamol", '.ng-binding', 0, 1).scrap())

            await task1
            await task2
            print("Teste Finalizado")
        else:
            selector = input("Entre o seletor:")
            should_print = int(
                input("Digite 1 para should_printar ou 0 para salvar num json:"))
            should_render = int(
                input("1 para prerenderizar pagina, 0 para nao:"))
            await ScrapTest(url_to_scrap, selector, should_print, should_render).scrap()

asyncio.run(main())
