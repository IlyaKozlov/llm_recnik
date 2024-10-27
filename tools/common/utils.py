import gzip
from typing import Iterable, TypeVar, List

import cyrtranslit


T = TypeVar('T')


def is_latin(text: str) -> bool:
    """
    Check if text is cyrillic or latin
    """
    cyrillic = "ертзуиопшђасдфгхјклчћжцвбнмђљњјџ"
    latin = "ǉǌertzuiopšđasdfghjklčćžǆcvbnm"
    cyrillic_cnt = sum(1 if L in text else 0 for L in cyrillic)
    latin_cnt = sum(1 if L in text else 0 for L in latin)
    return latin_cnt >= cyrillic_cnt


def to_cyrillic(text: str) -> str:
    return cyrtranslit.to_cyrillic(text, "sr")


def to_latin(text: str) -> str:
    return cyrtranslit.to_latin(text, "sr")


def batch(iterable: Iterable[T], size: int) -> Iterable[List[T]]:
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk


def wc(path: str) -> int:
    cnt = 0
    if path.endswith(".gz"):
        with gzip.open(path, "rb") as file:
            for _ in file:
                cnt += 1
    else:
        with open(path, "r") as file:
            for _ in file:
                cnt += 1
    return cnt
