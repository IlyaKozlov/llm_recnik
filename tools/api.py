import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from jinja2 import Template

from pydantic import BaseModel

from dictionary import get_translation

PORT = os.getenv("api_port", 8924)
app = FastAPI()

directory_path = Path(__file__).parent / "resources"

logger = logging.getLogger("converter_logger")


class Model(BaseModel):
    name: str


@app.get("/")
def root() -> HTMLResponse:
    path = directory_path / "intro.html"
    with open(path) as file:
        return HTMLResponse(content=file.read())


@app.get("/translate")
def list_models(word: str) -> HTMLResponse:
    result = get_translation(word)
    with open(directory_path / "translation.html") as file:
        template = Template(file.read())

    return HTMLResponse(template.render(word=word,
                                        norm=result["normal_form"],
                                        explanation=result["explanation"],
                                        translation=result["translation"],
                                        example=result["examples"]
                                        ))


@app.get("/translate_json")
def list_models(word: str) -> JSONResponse:
    return JSONResponse(content=get_translation(word))


@app.get("/favicon.ico")
def root() -> FileResponse:
    path = directory_path / "mascot.ico"
    return FileResponse(path=path)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=int(PORT))
