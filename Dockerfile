FROM python:3.11.9-slim-bullseye

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD inverted_dict.sqlite .

ADD tools /tools

ENV PYTHONPATH=/tools

CMD python3 /tools/api.py
