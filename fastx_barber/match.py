"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from fastx_barber.seqio import SimpleFastxRecord
from rich.progress import track  # type: ignore
from typing import Any, Dict, Iterator, List, Match, Optional, Pattern, Tuple, Union


class ANPMatch(object):
    __pattern: str
    __match: str
    __spans: List[Tuple[int, int]]
    __groups: List[str]
    __names: List[str]
    __groupdict: Dict[str, str]

    def __init__(
        self,
        match: str,
        span: Tuple[int, int],
        groups: List[Tuple[str, Tuple[int, int]]],
        pattern: str,
    ):
        super(ANPMatch, self).__init__()
        self.__pattern = pattern
        self.__match = match
        self.__spans = [span]
        self.__groups = [self.__match]
        self.__names = [""]
        self.__populate_groups(groups)

    def __populate_groups(self, groups: List[Tuple[str, Tuple[int, int]]]):
        for name, span in groups:
            self.__names.append(name)
            self.__spans.append(span)
            self.__groups.append(self.__match[span[0] : span[1]])

    @property
    def lastindex(self) -> int:
        return len(self.__groups)

    @property
    def lastgroup(self) -> str:
        return self.__names[-1]

    @property
    def pos(self) -> int:
        return self.start(None)

    @property
    def re(self):
        return self.__pattern

    def group(self, i: Optional[int]) -> str:
        if i is None:
            i = 0
        if i >= len(self.__spans):
            raise IndexError("no such group")
        return self.__groups[i]

    def groups(self) -> List[str]:
        return self.__groups[1:]

    def start(self, i: Optional[int]) -> int:
        if i is None:
            i = 0
        if i >= len(self.__spans):
            raise IndexError("no such group")
        return self.__spans[i][0]

    def end(self, i: Optional[int]) -> int:
        if i is None:
            i = 0
        if i >= len(self.__spans):
            raise IndexError("no such group")
        return self.__spans[i][1]

    def groupdict(self) -> Dict[str, str]:
        return dict(zip(self.__names[1:], self.__groups[1:]))


class AlphaNumericPattern(object):
    _pattern: str
    _length: int
    _groups: List[Tuple[str, Tuple[int, int]]]

    def __init__(self, pattern: str):
        super(AlphaNumericPattern, self).__init__()
        self._pattern = pattern
        self._groups = self.parse(pattern)
        self._length = sum([e - s for n, (s, e) in self._groups])

    @property
    def pattern(self):
        return self._pattern

    def match(self, query: str) -> Optional[ANPMatch]:
        if len(query) < self._length:
            return None
        return ANPMatch(
            query[: self._length], (0, self._length), self._groups, self._pattern
        )

    @staticmethod
    def remove_leading_digits(pattern: str) -> str:
        while pattern[0].isdigit():
            pattern = pattern[1:]
        return pattern

    @staticmethod
    def remove_trailing_alphas(pattern: str) -> str:
        while pattern[-1].isalpha():
            pattern = pattern[:-1]
        return pattern

    @staticmethod
    def parse(pattern: str) -> List[Tuple[str, Tuple[int, int]]]:
        assert pattern.isalnum()
        pattern = AlphaNumericPattern.remove_leading_digits(pattern)
        pattern = AlphaNumericPattern.remove_trailing_alphas(pattern)

        groups: Dict[str, Tuple[int, int]] = {}
        group_name = ""
        group_len = ""
        position = 0
        for c in pattern:
            if c.isalpha():
                if 0 != len(group_len):
                    assert group_name not in groups
                    groups[group_name] = (position, position + int(group_len))
                    position += int(group_len)
                    group_name = ""
                    group_len = ""
                group_name += c
            else:
                group_len += c
        groups[group_name] = (position, position + int(group_len))

        return sorted(groups.items(), key=lambda x: x[1][0])

    @staticmethod
    def to_regex(pattern: str) -> str:
        pattern_re = "^"
        for name, (start, end) in AlphaNumericPattern.parse(pattern):
            pattern_re += "(?<{name}>.{{end-start}})"
        return pattern_re

    def as_regex(self) -> str:
        return self.to_regex(self._pattern)


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

    def __init__(self, pattern: Union[AlphaNumericPattern, Pattern]):
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
    def do(self, record: Any) -> Tuple[Union[Optional[ANPMatch], Match], bool]:
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
    def __init__(self, pattern: Union[AlphaNumericPattern, Pattern]):
        super(FastxMatcher, self).__init__(pattern)

    def do(
        self, record: SimpleFastxRecord
    ) -> Tuple[Union[Optional[ANPMatch], Match], bool]:
        name, seq, _ = record
        match = self._pattern.match(seq)
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
        if seq[i : (i + len(needle))] == needle:
            match_counter += 1
            yield (i, match_counter)
