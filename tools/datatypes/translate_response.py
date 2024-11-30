from typing import Union

from pydantic import BaseModel

current_version = "1"


class TranslateResponse(BaseModel):
    html: str
    version: str
