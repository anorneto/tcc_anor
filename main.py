import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

from app.models.Crawlers import AsyncScrapper, AutoScrapper

app = FastAPI()


@app.get("/teste")
async def testeRoute():
    ascrapper = AsyncScrapper(
        url='https://hardmob.com.br/promocoes/', selectors='h3.threadtitle')
    response = await ascrapper.scrap()
    return JSONResponse(content=response)


class ScrapConfig(BaseModel):
    url: str
    selectors: Dict[str, str]
    render: bool = False


class MultiScrapConfig(BaseModel):
    sites: List[ScrapConfig]


class AutoScrapConfig(BaseModel):
    config_name: str
    base_url: str
    strings: Dict[str, str]
    render_page: bool = False
    list_url: List[str] = []


@app.post("/site")
async def siteRoute(scrapConfig: ScrapConfig):
    ascrapper = AsyncScrapper(scrapConfig.url, scrapConfig.selectors)
    response = await ascrapper.scrap()
    return JSONResponse(content=response)


@app.post("/multisite")
async def multisiteRoute(multiConfig: MultiScrapConfig):
    scrappersList = []
    for scrapConfig in multiConfig.sites:
        scrappersList.append(AsyncScrapper(
            url=scrapConfig.url, selectors=scrapConfig.selectors, render_page=scrapConfig.render or False))

    done = await asyncio.gather(*[scrapper.scrap() for scrapper in scrappersList])

    return JSONResponse(content=[done])


@app.post("/auto")
async def autoRoute(autoConfig: AutoScrapConfig):
    auto_scrapper = AutoScrapper(config_name=autoConfig.config_name,
                                 url=autoConfig.base_url, render_page=autoConfig.render_page, strings=autoConfig.strings)
    scrap_result = await auto_scrapper.scrap()

    if autoConfig.list_url:
        scrappersList = []
        selectors = dict()
        for key in scrap_result["selectors"]:
            selectors[key] = scrap_result["selectors"][key]["full"]
        for url in autoConfig.list_url:
            scrappersList.append(AsyncScrapper(
                url=url, selectors=selectors, render_page=scrap_result["render_page"] or False))

        done = await asyncio.gather(*[scrapper.scrap() for scrapper in scrappersList])
        return JSONResponse(content=done)
    else:
        return JSONResponse(content=scrap_result)


@app.post("/selectors")
async def selectorsRoute(autoConfig: AutoScrapConfig):
    auto_scrapper = AutoScrapper(config_name=autoConfig.config_name,
                                 url=autoConfig.base_url, strings=autoConfig.strings)
    response = await auto_scrapper.scrap()
    return JSONResponse(content=response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
