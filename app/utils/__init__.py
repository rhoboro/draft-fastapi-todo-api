import itertools
from collections.abc import Generator, Iterable
from typing import TypeVar

T = TypeVar("T")


def get_chunk(
    iterable: Iterable[T], n: int = 5
) -> Generator[Iterable[T], None, None]:
    for i, item in itertools.groupby(
        enumerate(iterable), lambda x: x[0] // n
    ):
        yield (x[1] for x in item)
