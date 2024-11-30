import json
import logging
from typing import Iterator

from jinja2 import Template

from context_tools.inverted_dict import InvertedDict
from datatypes.translate_response import TranslateResponse, current_version
from llm_tools.base_llm import BaseLLM
from llm_tools.cache import Cache

from llm_tools.stream_wrapper import StreamWrapper

logger = logging.getLogger(__name__)


class Translator(BaseLLM):

    def __init__(self, api_key: str):
        super().__init__(api_key)

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
        cache = Cache()
        value = cache.get(text.lower())
        if value is None or value.version != current_version:
            logger.info("Read response from llm")
            return self._from_llm(text)
        else:
            logger.info("Read response from cache")
            return [value.html].__iter__()

    def _from_llm(self, word: str) -> Iterator[str]:
        context = self._get_context(word)
        if self._is_latin(word):
            dir_path = self.prompt_latin
        else:
            dir_path = self.prompt_cyrillic
        path = dir_path / "dictionary_stream.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=word, context=context)
        stream = StreamWrapper(self.llm.stream(prompt))
        yield from self._yield_stream(stream)
        text = "".join(m.content for m in stream.cache)
        html = "\n".join(line for line in text.splitlines() if not line.strip().startswith("```"))
        to_cache = TranslateResponse(html=html, version=current_version)
        cache = Cache()
        cache.put(key=word.lower(), value=to_cache)
