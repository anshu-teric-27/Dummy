from pydantic import BaseModel
from typing import Optional


class DemoItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class DemoCreate(BaseModel):
    name: str
    description: Optional[str] = None

