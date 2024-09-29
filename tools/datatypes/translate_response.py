from typing import Union

from pydantic import BaseModel


class TranslateResponse(BaseModel):
    normal_form: str
    explanation: str
    translation: str
    examples: Union[str, dict]
