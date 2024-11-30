from typing import TypeVar, Iterable, Iterator

T = TypeVar("T")


class StreamWrapper(Iterator[T]):

    def __init__(self, stream: Iterator[T]) -> None:
        self.cache = []
        self._stream = stream

    def __next__(self) -> T:
        next_item = next(self._stream)
        self.cache.append(next_item)
        return next_item
