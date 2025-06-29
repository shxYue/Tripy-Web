from pydantic import BaseModel
from typing import Optional

class Blog(BaseModel):
    id: int
    title: str
    content: str
    author: Optional[str] = None