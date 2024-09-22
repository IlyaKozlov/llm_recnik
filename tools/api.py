import json
import logging
import os
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from jinja2 import Template

from pydantic import BaseModel

from datatypes.check_input import CheckInput
from dictionary import get_translation
from error_fixing import ErrorFixing
from translator import Translator

PORT = os.getenv("api_port", 8924)
app = FastAPI()

directory_path = Path(__file__).parent / "resources"

logger = logging.getLogger("converter_logger")
api_key = os.getenv("OPENAI_API_KEY")
translator = Translator(api_key=api_key)
error_fix = ErrorFixing(api_key=api_key)


class Model(BaseModel):
    name: str


@app.get("/")
def root() -> HTMLResponse:
    path = directory_path / "intro.html"
    with open(path) as file:
        return HTMLResponse(content=file.read())


@app.get("/check_form")
def root() -> HTMLResponse:
    path = directory_path / "check_form.html"
    with open(path) as file:
        return HTMLResponse(content=file.read())


@app.post("/check")
def check(text: str = Form(...)) -> HTMLResponse:
    text_with_fix = error_fix.fix(text=text)
    result = []
    for line in text_with_fix.split("\n"):
        result.append(f"<p>{line}</p>")
    with open(directory_path / "check_output.html") as file:
        template = Template(file.read())
    result_html = template.render(output="\n".join(result), original=text)
    return HTMLResponse(content=result_html)


@app.get("/mascot.jpg")
def get_mascot() -> FileResponse:
    path = directory_path / "mascot.jpg"
    return FileResponse(path=path)


@app.get("/translate")
def translate(word: str) -> HTMLResponse:
    print(f"get word: {word}")
    result = translator.translate(word)
    with open(directory_path / "translation.html") as file:
        template = Template(file.read())

    return HTMLResponse(template.render(word=word,
                                        norm=result["normal_form"],
                                        explanation=result["explanation"],
                                        translation=result["translation"],
                                        example=result["examples"]
                                        ))


@app.get("/translate_json")
def translate_json(word: str) -> JSONResponse:
    result = translator.translate(word)
    return JSONResponse(content=result)


@app.get("/favicon.ico")
def favicon() -> FileResponse:
    path = directory_path / "mascot.ico"
    return FileResponse(path=path)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=int(PORT))
