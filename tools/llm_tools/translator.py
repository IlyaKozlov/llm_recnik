import json

from jinja2 import Template

from datatypes.translate_response import TranslateResponse
from llm_tools.base_llm import BaseLLM


class Translator(BaseLLM):

    def translate(self, text: str) -> TranslateResponse:
        path = self.prompt_path / "dictionary.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=text)
        result = self.call_llm(prompt)
        price = result.price
        try:
            json.loads(result.content)
        except ValueError as error:
            print(f"try to fix json {error}")
            result = self.fix_json(
                result.content,
                error=str(error),
                schema=TranslateResponse.schema_json(indent=2),
            )
            price += result.price
        return TranslateResponse.model_validate_json(result.content)
