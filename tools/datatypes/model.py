from typing import Optional

from pydantic import BaseModel


class Model(BaseModel):
    name: str
    secret: Optional[str] = None
