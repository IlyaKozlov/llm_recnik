import json
import logging
from typing import Iterator

from jinja2 import Template

from context_tools.inverted_dict import InvertedDict
from datatypes.translate_response import TranslateResponse
from llm_tools.base_llm import BaseLLM
from llm_tools.cache import Cache

logger = logging.getLogger(__name__)


class Translator(BaseLLM):

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def translate(self, text: str) -> TranslateResponse:
        cache = Cache()
        cached = cache.get(text)
        if cached is None:
            logger.info("Not found in cache")
            llm_response = self._translate_with_llm(text)
            cache.put(key=text, value=llm_response)
            return llm_response
        else:
            logger.info("Got from cache")
            return cached

    def _translate_with_llm(self, text: str) -> TranslateResponse:
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

        logger.debug(result.content)

        try:
            TranslateResponse.model_validate_json(result.content)
        except Exception as error:
            logger.debug(f"try to fix json {error}")
            result = self.fix_json(
                result.content,
                error=str(error),
                schema=TranslateResponse.schema_json(indent=2),
            )
            price += result.price
        return TranslateResponse.model_validate_json(result.content)

    def _get_context(self, text: str) -> str:
        context_db = InvertedDict()
        context_list = context_db.get(text, [])
        if len(context_list) == 0:
            context = ""
        else:
            context = "\n\nCONTEXT:\n" + "\n".join(context_list)
        context = context.replace(text, text.upper())
        logger.debug(context)
        return context

    def translate_stream(self, text: str) -> Iterator[str]:
        context = self._get_context(text)
        if self._is_latin(text):
            dir_path = self.prompt_latin
        else:
            dir_path = self.prompt_cyrillic
        path = dir_path / "dictionary_stream.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=text, context=context)
        stream = self.llm.stream(prompt)
        yield from self._yield_stream(stream)
