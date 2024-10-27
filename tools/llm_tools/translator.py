import json

from jinja2 import Template

from context_tools.inverted_dict import InvertedDict
from datatypes.translate_response import TranslateResponse
from llm_tools.base_llm import BaseLLM


class Translator(BaseLLM):

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def translate(self, text: str) -> TranslateResponse:
        context = self._get_context(text)

        if self._is_latin(text):
            dir_path = self.prompt_latin
        else:
            dir_path = self.prompt_cyrillic
        path = dir_path / "dictionary.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=text, context=context)
        result = self.call_llm(prompt)
        price = result.price

        print(result.content)

        try:
            TranslateResponse.model_validate_json(result.content)
        except Exception as error:
            print(f"try to fix json {error}")
            result = self.fix_json(
                result.content,
                error=str(error),
                schema=TranslateResponse.schema_json(indent=2),
            )
            price += result.price
        return TranslateResponse.model_validate_json(result.content)

    def _get_context(self, text: str) -> str:
        context = InvertedDict()
        context_list = context.get(text, [])
        if len(context_list) == 0:
            context = ""
        else:
            context = "\n\nCONTEXT:\n" + "\n".join(context_list)
        context = context.replace(text, text.upper())
        print(context)
        return context
