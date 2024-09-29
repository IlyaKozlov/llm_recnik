import json
from abc import ABC

from jinja2 import Template
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from pathlib import Path


class LLMResponse(BaseModel):
    content: str
    price: float


class BaseLLM(ABC):
    price_input = 0.150 / 1e6  # price for input token
    price_output = 0.600 / 1e6
    prompt_path = Path(__file__).parent.parent / "templates"
    prompt_latin = prompt_path / "latin"
    cyrillic_path = prompt_path / "cyrillic"

    assert prompt_path.is_dir()

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

    def call_llm(self, prompt: str) -> LLMResponse:
        result = self.llm.invoke(prompt, temperature=0)

        price = (
                result.usage_metadata["input_tokens"] * self.price_input
                + result.usage_metadata["output_tokens"] * self.price_output
        )
        print(f"${price * 1000:0.2f} for 1000 calls \n\n\n")
        return LLMResponse(content=result.content, price=price)

    def fix_json(self, input_text: str, error: str, schema: str) -> LLMResponse:
        template_path = self.prompt_path / "fix_json.jinja"
        with open(template_path, "r") as file:
            template = Template(file.read())
        prompt = template.render(json=input_text, error=error, schema=schema)
        return self.call_llm(prompt)

