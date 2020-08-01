'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from abc import ABCMeta, abstractmethod
from fbarber.seqio import FastxSimpleRecord
from fbarber.const import FastxFormats
from typing import Any, List, Match, Optional, Tuple, Type

"""Flag data, contains name, matched str, start, and end position"""
FlagData = Tuple[str, str, int, int]


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
    def extract(self, record: Any, match: Match) -> List[FlagData]:
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

    def extract(self, record: FastxSimpleRecord, match: Match
                ) -> List[FlagData]:
        """Extract flags

        Arguments:
            record {FastxSimpleRecord} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        assert match is not None
        flag_data: List[FlagData] = []
        flags = list(match.groupdict().items())
        if self._selected_flags is not None:
            for gid in range(len(match.groups())):
                if flags[gid][0] in self._selected_flags:
                    flag_data.append(self.__extract_single_flag(match, gid))
        else:
            for gid in range(len(match.groups())):
                flag_data.append(self.__extract_single_flag(match, gid))
        return flag_data

    def __extract_single_flag(self, match: Match, gid: int,
                              flag: Optional[Tuple[str, str]] = None
                              ) -> FlagData:
        if flag is None:
            flag = list(match.groupdict().items())[gid]
        return (*flag, match.start(gid + 1), match.end(gid + 1))

    def update(self, record: FastxSimpleRecord, match: Match
               ) -> FastxSimpleRecord:
        """Update record

        Arguments:
            name {str} -- record to update based on flags
            match {Match} -- results of matching the record to a flag pattern
        """
        name, seq, _ = record
        name_bits = name.split(self._comment_space)
        for name, flag, start, end in self.extract(record, match):
            name_bits[0] += f"{self._flag_delim}{self._flag_delim}{name}"
            name_bits[0] += f"{self._flag_delim}{flag}"
        name = " ".join(name_bits)
        return (name, seq, None)


class FastqFlagExtractor(FastaFlagExtractor):
    """Fastq flag extractor class"""

    def __init__(self, selected_flags: Optional[List[str]] = None):
        """Initialize fastq file flag extractor

        Keyword Arguments:
            selected_flags {Optional[List[str]]} -- (default: {None})
        """
        super(FastqFlagExtractor, self).__init__(selected_flags)

    def extract(self, record: FastxSimpleRecord, match: Match
                ) -> List[FlagData]:
        """Extract flags

        Arguments:
            record {FastxSimpleRecord} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        flags = super(FastqFlagExtractor, self).extract(record, match)
        for name, flag, start, end in flags:
            group_slice = slice(start, end)
            flags.append((f"q{name}", qual[group_slice], start, end))
        return flags


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
