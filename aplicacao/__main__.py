import asyncio
import uvicorn

from typing import List, Dict
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic.main import BaseModel

from .models.Crawlers import AutoScrapper, AsyncScrapper

app = FastAPI()


class ScrapConfig(BaseModel):
    config_name: str
    base_url: str
    selectors: Dict[str, str]
    response_as_list: bool = False
    render_page: bool = False


class MultiScrapConfig(BaseModel):
    configs: List[ScrapConfig]


class AutoScrapConfig(BaseModel):
    config_name: str
    base_url: str
    strings: Dict[str, str]
    response_as_list: bool = False
    list_url: List[str] = []
    render_page: bool = False


@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=500, content={"message": f"{base_error_message}", "detail":  f"{err}"})


@app.post("/site")
async def siteRoute(scrapConfig: ScrapConfig):
    ascrapper = AsyncScrapper(config_name=scrapConfig.config_name, url=scrapConfig.base_url,
                              selectors=scrapConfig.selectors, render_page=scrapConfig.render_page, response_as_list=scrapConfig.response_as_list)
    response = await ascrapper.scrap()
    return JSONResponse(content=response)


@app.post("/multisite")
async def multisiteRoute(multiConfig: MultiScrapConfig):
    scrappersList = []
    for scrapConfig in multiConfig.configs:
        scrappersList.append(AsyncScrapper(config_name=scrapConfig.config_name,
                                           url=scrapConfig.base_url, selectors=scrapConfig.selectors,
                                           response_as_list=scrapConfig.response_as_list,
                                           render_page=scrapConfig.render_page or False))

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
            if scrap_result["selectors"][key]["last"] != "":
                selectors[key] = scrap_result["selectors"][key]["last"]
            else:
                selectors[key] = scrap_result["selectors"][key]["full"]
        for url in autoConfig.list_url:
            scrappersList.append(AsyncScrapper(config_name=autoConfig.config_name,
                                               url=url, selectors=selectors, response_as_list=autoConfig.response_as_list, render_page=autoConfig.render_page))

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


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
