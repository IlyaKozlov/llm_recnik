import json
import os
from json import JSONDecodeError
from pathlib import Path
from pprint import pprint

from jinja2 import Template
from langchain_openai import ChatOpenAI


api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

template_path = Path(__file__).parent / "templates/dictionary.jinja"

with open(template_path) as file_:
    template = Template(file_.read())


with open(template_path) as file_:
    json_template = Template(file_.read())


def call_llm(prompt: str) -> str:
    result = llm.invoke(prompt, temperature=0)

    price_input = 0.150 / 1e6
    price_output = 0.600 / 1e6
    price = (
        result.usage_metadata["input_tokens"] * price_input
        + result.usage_metadata["output_tokens"] * price_output
    )
    print(f"${price * 1000:0.2f} for 1000 calls \n\n\n")
    return result.content


def get_translation(word: str) -> dict:
    prompt = template.render(text=word)

    text = call_llm(prompt)

    try:
        json.loads(text)
    except JSONDecodeError as error:
        prompt_json = json_template.render(json=text, error=str(error))
        text = call_llm(prompt_json)
    return json.loads(text)


if __name__ == "__main__":
    pprint(get_translation("cimerka"))
