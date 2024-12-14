from typing import NamedTuple


class TelegramMessage(NamedTuple):
    entity_type: str
    text: str
