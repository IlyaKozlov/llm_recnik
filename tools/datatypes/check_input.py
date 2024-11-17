from typing import Optional

from pydantic import BaseModel


class CheckInput(BaseModel):

    text: str

    secret: Optional[str] = None
