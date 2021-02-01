from typing import List, Dict
from pydantic.main import BaseModel


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
