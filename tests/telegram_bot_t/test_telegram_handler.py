from pathlib import Path
from unittest import TestCase

from telegram_bot.telegram_handler import _stream2telegram


class TestTelegramHandler(TestCase):
    def test__stream2telegram(self):
        path = Path(__file__).parent / "input_example.txt"
        with open(path) as file:
            text = file.read()
        answer = list(_stream2telegram(text))
        self.assertEqual("Чинчила", answer[1].text.strip())
        self.assertEqual("Пример:", answer[7].text.strip())
