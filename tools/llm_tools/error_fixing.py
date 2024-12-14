from typing import Iterator

from jinja2 import Template

from llm_tools.base_llm import BaseLLM


class ErrorFixing(BaseLLM):

    def fix(self, text: str) -> str:
        prompt = self._get_prompt(text)
        result = self.call_llm(prompt)
        return result.content

    def fix_stream(self, text: str) -> Iterator[str]:
        prompt = self._get_prompt(text)
        stream = self.llm.stream(prompt)
        yield from self._yield_stream(stream)

    def _get_prompt(self, text: str) -> str:
        if self._is_latin(text):
            dir_path = self.prompt_latin
        else:
            dir_path = self.prompt_cyrillic
        path = dir_path / "check.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=text)
        return prompt
