from typing import Dict, List,Union
from pydantic import BaseModel


class ScrapResponse(BaseModel):
    config_name: str
    url: str
    render_page: bool = False
    headers: List[str] = None
    items: Union[Dict[str, List[str]], List[List[str]]]

class AutoScrapResponse(BaseModel):
    config_name: str
    url: str
    render_page: bool = False
    selectors: Dict[str, Dict[str,str]]
