import logging
from abc import ABC
from pathlib import Path
from typing import Iterator

from jinja2 import Template
from langchain_core.messages.base import BaseMessageChunk
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    content: str
    price: float


class BaseLLM(ABC):
    price_input = 0.150 / 1e6  # price for input token
    price_output = 0.600 / 1e6
    prompt_path = Path(__file__).parent.parent / "templates"
    prompt_latin = prompt_path / "latin"
    prompt_cyrillic = prompt_path / "cyrillic"

    assert prompt_path.is_dir()

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

    @staticmethod
    def _is_latin(text: str) -> bool:
        cyrillic = "ертзуиопшђасдфгхјклчћжцвбнмђљњјџ"
        latin = "ǉǌertzuiopšđasdfghjklčćžǆcvbnm"
        cyrillic_cnt = sum(1 if L in text else 0 for L in cyrillic)
        latin_cnt = sum(1 if L in text else 0 for L in latin)
        return latin_cnt >= cyrillic_cnt

    def call_llm(self, prompt: str) -> LLMResponse:
        result = self.llm.invoke(prompt, temperature=0)

        price = (
            result.usage_metadata["input_tokens"] * self.price_input
            + result.usage_metadata["output_tokens"] * self.price_output
        )
        logger.info(f"${price * 1000:0.2f} for 1000 calls \n\n\n")
        return LLMResponse(content=result.content, price=price)

    def fix_json(self, input_text: str, error: str, schema: str) -> LLMResponse:
        template_path = self.prompt_path / "fix_json.jinja"
        with open(template_path, "r") as file:
            template = Template(file.read())
        prompt = template.render(json=input_text, error=error, schema=schema)
        return self.call_llm(prompt)

    def _yield_stream(self, stream: Iterator[BaseMessageChunk]) -> Iterator[str]:
        output = ""
        right = 0
        for item in stream:
            output += item.content
            text_out = output.replace("```html", "").replace("`", "")
            text_out_patch = text_out[right:]
            if text_out_patch.endswith("\n"):
                yield text_out_patch
                right = len(text_out)
