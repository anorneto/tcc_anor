import asyncio
import uvicorn

from typing import List, Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from models.Crawlers import AutoScrapper, AsyncScrapper
from models.RequestConfig import ScrapConfig, AutoScrapConfig
from models.ResponseModels import ScrapResponse, AutoScrapResponse


app = FastAPI(title="TCC Anor",
              description="Web Scrapping API",
              version="1.0.0",)


@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=500, content={"message": f"{base_error_message}", "detail":  f"{err}"})


@app.post("/site", response_model=ScrapResponse)
async def siteRoute(scrapConfig: ScrapConfig):
    ascrapper = AsyncScrapper(config_name=scrapConfig.config_name, url=scrapConfig.base_url,
                              selectors=scrapConfig.selectors, render_page=scrapConfig.render_page, response_as_list=scrapConfig.response_as_list)
    response = await ascrapper.scrap()
    return JSONResponse(content=response)


@app.post("/multisite", response_model=List[ScrapResponse])
async def multisiteRoute(multiConfig: List[ScrapConfig]):
    scrappersList = []
    for scrapConfig in multiConfig:
        scrappersList.append(AsyncScrapper(config_name=scrapConfig.config_name,
                                           url=scrapConfig.base_url, selectors=scrapConfig.selectors,
                                           response_as_list=scrapConfig.response_as_list,
                                           render_page=scrapConfig.render_page or False))

    scrappersResult = await asyncio.gather(*[scrapper.scrap() for scrapper in scrappersList])

    return JSONResponse(content=scrappersResult)


@app.post("/auto", response_model=Union[AutoScrapResponse, List[ScrapResponse]])
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
            scrappersList.append(ScrapConfig(config_name=autoConfig.config_name,
                                             base_url=url, selectors=selectors, response_as_list=autoConfig.response_as_list, render_page=autoConfig.render_page))

        return await multisiteRoute(multiConfig=scrappersList)
    else:
        return JSONResponse(content=scrap_result)


""" @app.post("/selectors")
async def selectorsRoute(autoConfig: AutoScrapConfig):
    auto_scrapper = AutoScrapper(config_name=autoConfig.config_name,
                                 url=autoConfig.base_url, strings=autoConfig.strings)
    response = await auto_scrapper.scrap()
    return JSONResponse(content=response) """


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
