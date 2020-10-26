import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

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
    selectors: List[str]
    render: bool = False


class MultiScrapConfig(BaseModel):
    sites: List[ScrapConfig]


class AutoScrapConfig(BaseModel):
    url: str
    string_list: List[str]
    render: bool = False


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
    auto_scrapper = AutoScrapper(
        url=autoConfig.url, string_list=autoConfig.string_list)
    response = await auto_scrapper.scrap()
    return JSONResponse(content=[response])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
