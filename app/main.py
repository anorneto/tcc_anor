import asyncio
import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from requests_html import AsyncHTMLSession
from pydantic import BaseModel
from typing import List

from app.models.Crawlers import AsyncScrapper

app = FastAPI()


@app.get("/teste")
async def root():
    ascrapper = AsyncScrapper(url='https://hardmob.com.br/promocoes/',selectors='h3.threadtitle')
    response = await ascrapper.scrap()
    return JSONResponse(content=response)

class ScrapConfig(BaseModel):
    url: str
    selectors: str
    render: bool = False

class MultiScrapConfig(BaseModel):
    sites: List[ScrapConfig]

@app.post("/site")
async def root(scrapConfig : ScrapConfig):
    ascrapper = AsyncScrapper(scrapConfig.url,scrapConfig.selectors)
    response = await ascrapper.scrap()
    return JSONResponse(content=response)


@app.post("/multisite")
async def root(multiConfig: MultiScrapConfig):
    scrappersList = []
    for scrapConfig in multiConfig.sites:
        scrappersList.append( AsyncScrapper(url= scrapConfig.url,selectors= scrapConfig.selectors,render_page= scrapConfig.render or False))

    done = await asyncio.gather(*[scrapper.scrap() for scrapper in scrappersList])

    return JSONResponse(content=[done])
