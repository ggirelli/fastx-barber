'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from abc import ABCMeta, abstractmethod
from fbarber.seqio import FastxSimpleRecord
import regex  # type: ignore
from typing import Any, Match, Pattern, Tuple


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
    def match(self, record: Any) -> Tuple[Match, bool]:
        """Match a record with the provided pattern

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record to be matched
        """
        pass


class FastxMatcher(ABCMatcher):
    """Fastx record matcher class

    Extends:
        ABCMatcher
    """

    def __init__(self, pattern: Pattern):
        """Init fastx matcher class

        Arguments:
            pattern {Pattern} -- pattern to be matched
        """
        super(FastxMatcher, self).__init__(pattern)

    def match(self, record: FastxSimpleRecord
              ) -> Tuple[Match, bool]:
        """Match a record with the provided pattern

        Arguments:
            record {FastxSimpleRecord} -- record to be matched
        """
        name, seq, _ = record
        match = regex.match(self._pattern, seq)
        matched = match is not None
        if matched:
            self._matched_count += 1
        else:
            self._unmatched_count += 1
        return (match, matched)
