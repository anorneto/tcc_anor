from typing import Dict, List
from pydantic import BaseModel


class ScrapConfig(BaseModel):
    config_name: str
    base_url: str
    selectors: Dict[str, str]
    response_as_list: bool = False
    headers: List[str] = None
    render_page: bool = False


class AutoScrapConfig(BaseModel):
    config_name: str
    base_url: str
    strings: Dict[str, str]
    response_as_list: bool = False
    render_page: bool = False
    list_url: List[str] = []
