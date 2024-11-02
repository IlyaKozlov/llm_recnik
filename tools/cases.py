import logging
from pathlib import Path

from dotenv import dotenv_values
from jinja2 import Template
from langchain_openai import ChatOpenAI

config_path = Path(__file__).parent.parent.parent / ".env"
config = dotenv_values(config_path)
logger = logging.getLogger(__name__)
api_key = config["OPENAI_API_KEY"]

llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

template_path = "cases.jinja"

with open(template_path) as file_:
    template = Template(file_.read())

prompt = template.render(text="Čovek koji sa prozora baca pare i neće da sluša naređenja: Ko je Pavel Durov, osnivač Telegrama koji je uhapšen u Francuskoj")
result = llm.invoke(prompt, temperature=0).content

logger.info(result)
