from pydantic import BaseModel


class CheckInput(BaseModel):

    text: str
