import logging
import os
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from jinja2 import Template

from llm_tools.error_fixing import ErrorFixing
from llm_tools.translator import Translator
from token_utils import check_access

PORT = os.getenv("PORT", 8924)
app = FastAPI()

directory_path = Path(__file__).parent / "resources"

logger = logging.getLogger("converter_logger")
api_key = os.getenv("OPENAI_API_KEY")
translator = Translator(api_key=api_key)
error_fix = ErrorFixing(api_key=api_key)


def add_secret(html_path: Path, secret: str) -> str:
    with open(html_path, "r") as f:
        template = Template(f.read())
    return template.render(secret=secret)


@app.get("/")
def root(secret: Optional[str] = None) -> HTMLResponse:
    if not check_access(secret):
        return access_denied()
    path = directory_path / "intro.html"
    content = add_secret(path, secret)
    return HTMLResponse(content=content)


@app.get("/check_form")
def check_form(secret: Optional[str] = None) -> HTMLResponse:
    if not check_access(secret):
        return access_denied()
    path = directory_path / "check_form.html"
    content = add_secret(path, secret)
    return HTMLResponse(content=content)


@app.post("/check")
def check(text: str = Form(...), secret: Optional[str] = Form(default=None)) -> HTMLResponse:
    if not check_access(secret):
        return access_denied()
    text_with_fix = error_fix.fix(text=text)
    result = []
    for line in text_with_fix.split("\n"):
        result.append(f"<p>{line}</p>")
    with open(directory_path / "check_output.html") as file:
        template = Template(file.read())
    result_html = template.render(output="\n".join(result), original=text)
    return HTMLResponse(content=result_html)


@app.get("/mascot.jpg")
def get_mascot(secret: Optional[str] = None) -> FileResponse:
    path = directory_path / "mascot.jpg"
    return FileResponse(path=path)


def access_denied() -> HTMLResponse:
    with open(directory_path / "access_denied.html") as file:
        template = Template(file.read())
        contacts = os.environ.get("MAINTAINER_CONTACTS", "")
        return HTMLResponse(content=template.render(maintainer=contacts))


@app.get("/translate")
def translate(word: str, secret: Optional[str] = None) -> HTMLResponse:
    if not check_access(secret):
        return access_denied()
    print(f"get word: {word}")
    result = translator.translate(word)
    with open(directory_path / "translation.html") as file:
        template = Template(file.read())

    return HTMLResponse(template.render(word=word,
                                        norm=result.normal_form,
                                        explanation=result.explanation,
                                        translation=result.translation,
                                        example=result.examples
                                        ))


@app.get("/translate_json")
def translate_json(word: str, secret: Optional[str] = None) -> JSONResponse:
    if not check_access(secret):
        return JSONResponse(content={"status": "access denied"}, status_code=403)
    result = translator.translate(word)
    return JSONResponse(content=result)


@app.get("/favicon.ico")
def favicon(secret: Optional[str] = None) -> FileResponse:
    path = directory_path / "mascot.ico"
    return FileResponse(path=path)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=int(PORT))
