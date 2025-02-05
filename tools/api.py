import logging
import os
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.responses import StreamingResponse
from jinja2 import Template

from datatypes.check_input import CheckInput
from datatypes.translate_input import TranslateInput
from llm_tools.error_fixing import ErrorFixing
from llm_tools.translator import Translator
from token_utils import check_access
from utils import init_logger

PORT = os.getenv("PORT", 8924)
app = FastAPI()

directory_path = Path(__file__).parent / "resources"


api_key = os.getenv("OPENAI_API_KEY")
translator = Translator(api_key=api_key)
error_fix = ErrorFixing(api_key=api_key)


init_logger()

logger = logging.getLogger("converter_logger")


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


@app.post("/check")
def check(
    text: str = Form(...), secret: Optional[str] = Form(default=None)
) -> HTMLResponse:
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


@app.post("/translate_stream")
def translate(parameters: TranslateInput) -> StreamingResponse:
    if not check_access(parameters.secret):
        return access_denied()
    return StreamingResponse(
        translator.translate_stream(text=parameters.word),
        media_type="text/event-stream",
    )


@app.get("/favicon.ico")
def favicon(secret: Optional[str] = None) -> FileResponse:
    path = directory_path / "mascot.ico"
    return FileResponse(path=path)


@app.post("/stream_fix_text")
def streaming_post(data: CheckInput):
    pass
    if check_access(data.secret):
        return StreamingResponse(
            error_fix.fix_stream(text=data.text), media_type="text/event-stream"
        )
    return access_denied()


@app.get("/check_form")
def for_stream(secret: Optional[str] = None):
    with open(directory_path / "check_output_stream.html") as file:
        template = Template(file.read())
        return HTMLResponse(template.render(secret=secret))


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=int(PORT))
