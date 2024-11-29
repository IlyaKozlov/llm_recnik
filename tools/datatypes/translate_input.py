from typing import Optional

from pydantic import BaseModel


class TranslateInput(BaseModel):
    word: str
    secret: Optional[str] = None
