import json
from json import JSONDecodeError

from jinja2 import Template

from base_llm import BaseLLM


class Translator(BaseLLM):

    def translate(self, text: str) -> dict:
        path = self.prompt_path / "dictionary.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=text)
        result = self.call_llm(prompt)
        price = result.price
        try:
            json.loads(result.content)
        except JSONDecodeError as error:
            print(f"try to fix json {error}")
            result = self.fix_json(result.content, error=str(error))
            price += result.price
        return json.loads(result.content)
