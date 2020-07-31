'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from abc import ABCMeta, abstractmethod
from fbarber.seqio import FastxSimpleRecord
from fbarber.const import FastxFormats
import regex  # type: ignore
from typing import Pattern, Match, Optional, Tuple, Type


class ABCFlagExtractor(metaclass=ABCMeta):
    """Flag extractor abstract base class"""

    _matched_count: int = 0
    _unmatched_count: int = 0

    def __init__(self, pattern: Pattern,
                 flag_delim: str = "~",
                 comment_space: str = " "):
        self._pattern = pattern
        assert 1 == len(flag_delim)
        self._delim = flag_delim
        assert 1 == len(comment_space)
        self._comment_space = comment_space

    @property
    def matched_count(self) -> int:
        return self._matched_count

    @property
    def unmatched_count(self) -> int:
        return self._unmatched_count

    @property
    def parsed_count(self) -> int:
        return self._matched_count + self._unmatched_count

    @abstractmethod
    def extract(self, record: FastxSimpleRecord
                ) -> Tuple[FastxSimpleRecord, bool]: pass

    @abstractmethod
    def _update_name(self, name: str, match: Match,
                     qual: Optional[str] = None) -> str: pass


class FastaFlagExtractor(ABCFlagExtractor):
    """Fasta flag extractor class"""

    def __init__(self, pattern: Pattern,
                 flag_delim: str = "~",
                 comment_space: str = " "):
        super(FastaFlagExtractor, self).__init__(
            pattern, flag_delim, comment_space)

    def extract(self, record: FastxSimpleRecord
                ) -> Tuple[FastxSimpleRecord, bool]:
        name, seq, _ = record
        match = regex.match(self._pattern, seq)
        if match is None:
            self._unmatched_count += 1
            return (record, False)
        else:
            seq = regex.sub(self._pattern, "", seq)
            name = self._update_name(name, match)
            self._matched_count += 1
            return ((name, seq, None), True)

    def _update_name(self, name: str, match: Match,
                     qual: Optional[str] = None) -> str:
        name_bits = name.split(self._comment_space)
        for label, value in match.groupdict().items():
            name_bits[0] += f"{self._delim}{self._delim}{label}"
            name_bits[0] += f"{self._delim}{value}"
        name = " ".join(name_bits)
        return name


class FastqFlagExtractor(FastaFlagExtractor):
    """Fastq flag extractor class"""

    def __init__(self, pattern: Pattern,
                 flag_delim: str = "~",
                 comment_space: str = " "):
        super(FastqFlagExtractor, self).__init__(
            pattern, flag_delim, comment_space)

    def extract(self, record: FastxSimpleRecord
                ) -> Tuple[FastxSimpleRecord, bool]:
        name, seq, qual = record
        assert qual is not None
        match = regex.match(self._pattern, seq)
        if match is None:
            self._unmatched_count += 1
            return (record, False)
        else:
            seq = regex.sub(self._pattern, "", seq)
            name = self._update_name(name, match, qual)
            qual = qual[-len(seq):]
            self._matched_count += 1
            return ((name, seq, qual), True)

    def _update_name(self, name: str, match: Match,
                     qual: Optional[str] = None) -> str:
        name = super(FastqFlagExtractor, self)._update_name(name, match)
        if qual is not None:
            qual_bits = ""
            flags = list(match.groupdict().keys())
            for gid in range(len(match.groups())):
                group_name = flags[gid]
                group_qual = qual[match.start(gid + 1):match.end(gid + 1)]
                qual_bits += f"{self._delim}{self._delim}q{group_name}"
                qual_bits += f"{self._delim}{group_qual}"
            name += qual_bits
        return name


def get_fastx_flag_extractor(fmt: FastxFormats) -> Type[ABCFlagExtractor]:
    if FastxFormats.FASTA == fmt:
        return FastaFlagExtractor
    elif FastxFormats.FASTQ == fmt:
        return FastqFlagExtractor
    else:
        return ABCFlagExtractor
