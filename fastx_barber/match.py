"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from fastx_barber.seqio import SimpleFastxRecord
import regex as re  # type: ignore
from rich.progress import track  # type: ignore
from typing import Any, Iterator, Match, Pattern, Tuple


class ABCMatcher(metaclass=ABCMeta):
    """Record matcher abstract base class

    Extends:
        metaclass=ABCMeta

    Variables:
        _matched_count {int} -- number of matched records
        _unmatched_count {int} -- number of unmatched records
    """

    _matched_count: int = 0
    _unmatched_count: int = 0

    def __init__(self, pattern: Pattern):
        """Init matcher class

        Arguments:
            pattern {Pattern} -- pattern to be matched
        """
        self._pattern = pattern

    @property
    def matched_count(self) -> int:
        return self._matched_count

    @property
    def unmatched_count(self) -> int:
        return self._unmatched_count

    @abstractmethod
    def do(self, record: Any) -> Tuple[Match, bool]:
        """Match a record with the provided pattern

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record to be matched

        Returns:
            Tuple[Match, bool] -- match and matched status
        """
        pass


class FastxMatcher(ABCMatcher):
    def __init__(self, pattern: Pattern):
        super(FastxMatcher, self).__init__(pattern)

    def do(self, record: SimpleFastxRecord) -> Tuple[Match, bool]:
        name, seq, _ = record
        match = re.match(self._pattern, seq)
        matched = match is not None
        if matched:
            self._matched_count += 1
        else:
            self._unmatched_count += 1
        return (match, matched)


def search_needle(
    record: SimpleFastxRecord, needle: str, offset: int = 0
) -> Iterator[Tuple[int, int]]:
    header, seq, _ = record
    match_counter = offset
    for i in track(range(0, len(seq) - len(needle) + 1), description=header):
        if seq[i: (i + len(needle))] == needle:
            match_counter += 1
            yield (i, match_counter)
