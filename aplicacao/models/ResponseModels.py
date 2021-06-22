from typing import Dict, List
from pydantic import BaseModel


class ScrapResponse(BaseModel):
    config_name: str
    url: str
    render_page: bool = False
    headers: List[str] = None
    itens: Dict[str, str]


class AutoScrapResponse(BaseModel):
    config_name: str
    url: str
    render_page: bool = False
    selectors: Dict[str, Dict[str,str]]
