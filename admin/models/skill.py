from pydantic import BaseModel, Field
from typing import Optional, Any


class SkillCreateRequest(BaseModel):
    frontmatter: dict = {}
    body: str = ""


class SkillUpdateRequest(BaseModel):
    frontmatter: dict = {}
    body: str = ""
