from pydantic import BaseModel
from typing import Optional


class PluginCreateRequest(BaseModel):
    name: str
    description: str
    category: str = "general"
    keywords: list = []


class PluginUpdateRequest(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[list] = None
