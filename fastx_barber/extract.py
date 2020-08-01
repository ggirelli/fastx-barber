"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from fastx_barber.seqio import FastxSimpleRecord
from fastx_barber.const import FastxFormats
from typing import Any, Dict, List, Match, Optional, Tuple, Type

"""Flag data, contains matched str, start, and end position"""
FlagData = Tuple[str, int, int]


class ABCFlagExtractor(metaclass=ABCMeta):
    """Flag extractor abstract base class

    Extends:
        metaclass=ABCMeta

    Variables:
        _flag_delim {str} -- flag delimiter
        _comment_space {str} -- fastx comment separator
        _selected_flags {Optional[List[str]]} -- flags to extract
    """

    _flag_delim: str = "~"
    _comment_space: str = " "
    _selected_flags: Optional[List[str]] = None

    def __init__(self, selected_flags: Optional[List[str]] = None):
        """Initialize flag extractor

        Keyword Arguments:
            selected_flags {Optional[List[str]]} -- (default: {None})
        """
        self._selected_flags = selected_flags

    @property
    def flag_delim(self):
        return self._flag_delim

    @flag_delim.setter
    def flag_delim(self, flag_delim: str):
        assert 1 == len(flag_delim)
        self._flag_delim = flag_delim

    @property
    def comment_space(self):
        return self._flag_delim

    @comment_space.setter
    def comment_space(self, comment_space: str):
        assert 1 == len(comment_space)
        self._comment_space = comment_space

    @abstractmethod
    def extract(self, record: Any, match: Match) -> Dict[str, FlagData]:
        """Extract flags (according to self._selected_flags)

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        pass

    @abstractmethod
    def update(self, record: Any, match: Match) -> Any:
        """Update record

        Decorators:
            abstractmethod

        Arguments:
            name {str} -- record to update based on flags
            match {Match} -- results of matching the record to a flag pattern
        """
        pass


class FastaFlagExtractor(ABCFlagExtractor):
    """Fasta flag extractor class"""

    def __init__(self, selected_flags: Optional[List[str]] = None):
        """Initialize fasta file flag extractor

        Keyword Arguments:
            selected_flags {Optional[List[str]]} -- (default: {None})
        """
        super(FastaFlagExtractor, self).__init__(selected_flags)

    def extract(self, record: FastxSimpleRecord, match: Match) -> Dict[str, FlagData]:
        """Extract flags

        Arguments:
            record {FastxSimpleRecord} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        assert match is not None
        flag_data: Dict[str, FlagData] = {}
        flag_info = list(match.groupdict().items())
        if self._selected_flags is not None:
            for gid in range(len(match.groups())):
                if flag_info[gid][0] in self._selected_flags:
                    flag = self.__extract_single_flag(match, gid)
                    flag_data.update([flag])
        else:
            for gid in range(len(match.groups())):
                flag = self.__extract_single_flag(match, gid)
                flag_data.update([flag])
        return flag_data

    def __extract_single_flag(
        self, match: Match, gid: int, flag: Optional[Tuple[str, str]] = None
    ) -> Tuple[str, FlagData]:
        if flag is None:
            flag = list(match.groupdict().items())[gid]
        return (flag[0], (flag[1], match.start(gid + 1), match.end(gid + 1)))

    def update(self, record: FastxSimpleRecord, match: Match) -> FastxSimpleRecord:
        """Update record

        Arguments:
            name {str} -- record to update based on flags
            match {Match} -- results of matching the record to a flag pattern
        """
        name, seq, _ = record
        name_bits = name.split(self._comment_space)
        for name, (flag, start, end) in self.extract(record, match).items():
            name_bits[0] += f"{self._flag_delim}{self._flag_delim}{name}"
            name_bits[0] += f"{self._flag_delim}{flag}"
        name = " ".join(name_bits)
        return (name, seq, None)


class FastqFlagExtractor(FastaFlagExtractor):
    """Fastq flag extractor class"""

    extract_qual_flags: bool = True

    def __init__(self, selected_flags: Optional[List[str]] = None):
        """Initialize fastq file flag extractor

        Keyword Arguments:
            selected_flags {Optional[List[str]]} -- (default: {None})
        """
        super(FastqFlagExtractor, self).__init__(selected_flags)

    def extract(self, record: FastxSimpleRecord, match: Match) -> Dict[str, FlagData]:
        """Extract flags

        Arguments:
            record {FastxSimpleRecord} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        flag_data = super(FastqFlagExtractor, self).extract(record, match)
        if self.extract_qual_flags:
            for name, (_, start, end) in list(flag_data.items()):
                flag = (f"q{name}", (qual[slice(start, end)], start, end))
                flag_data.update([flag])
        return flag_data

    def update(self, record: FastxSimpleRecord, match: Match) -> FastxSimpleRecord:
        """Update record

        Arguments:
            name {str} -- record to update based on flags
            match {Match} -- results of matching the record to a flag pattern
        """
        _, _, qual = record
        name, seq, _ = super(FastqFlagExtractor, self).update(record, match)
        return (name, seq, qual)


def get_fastx_flag_extractor(fmt: FastxFormats) -> Type[ABCFlagExtractor]:
    """Retrieves appropriate flag extractor class.

    Arguments:
        fmt {FastxFormats}

    Returns:
        Type[ABCFlagExtractor] -- flag extractor class
    """
    if FastxFormats.FASTA == fmt:
        return FastaFlagExtractor
    elif FastxFormats.FASTQ == fmt:
        return FastqFlagExtractor
    else:
        return ABCFlagExtractor
