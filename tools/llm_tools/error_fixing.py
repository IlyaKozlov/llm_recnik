from jinja2 import Template

from llm_tools.base_llm import BaseLLM


class ErrorFixing(BaseLLM):

    def fix(self, text: str) -> str:
        if self._is_latin(text):
            dir_path = self.prompt_latin
        else:
            dir_path = self.prompt_cyrillic
        path = dir_path / "check.jinja"
        with open(path, "r") as file:
            template = Template(file.read())
        prompt = template.render(text=text)
        result = self.call_llm(prompt)
        return result.content
