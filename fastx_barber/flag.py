"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from fastx_barber.const import FastxFormats, QFLAG_START
from fastx_barber.seqio import SimpleFastxRecord
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
    def extract_selected(self, record: Any, match: Match) -> Dict[str, FlagData]:
        """Extract selected flags

        Flags are selected according to self._selected_flags

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern

        Returns:
            Dict[str, FlagData] -- a dictionary with flag name as key and data as value
        """
        pass

    @abstractmethod
    def extract_all(self, record: Any, match: Match) -> Dict[str, FlagData]:
        """Extract all flags

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern

        Returns:
            Dict[str, FlagData] -- a dictionary with flag name as key and data as value
        """
        pass

    @abstractmethod
    def update(self, record: Any, flag_data: Dict[str, FlagData]) -> Any:
        """Update record

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record to update based on flags
            flag_data {Dict[str, FlagData]} -- a dictionary with flag name as key
                                               and data as value

        Returns:
            Any -- updated record.
        """
        pass

    def apply_selection(self, flag_data: Dict[str, FlagData]) -> Dict[str, FlagData]:
        """Subselects provided flags.

        According to self._selected_flags

        Decorators:
            abstractmethod

        Arguments:
            flag_data {Dict[str, FlagData]} -- a dictionary with flag name as key
                                               and data as value
        """
        if self._selected_flags is None:
            return flag_data
        else:
            selected_flag_data = {}
            for name in self._selected_flags:
                if name in flag_data.keys():
                    selected_flag_data[name] = flag_data[name]
            return selected_flag_data


class FastaFlagExtractor(ABCFlagExtractor):
    def __init__(self, selected_flags: Optional[List[str]] = None):
        super(FastaFlagExtractor, self).__init__(selected_flags)

    def extract_selected(
        self, record: SimpleFastxRecord, match: Match
    ) -> Dict[str, FlagData]:
        assert match is not None
        flag_data: Dict[str, FlagData] = {}
        flag_data_all = self.extract_all(record, match)
        if self._selected_flags is not None:
            for flag, data in flag_data_all.items():
                if flag in self._selected_flags:
                    flag_data[flag] = data
        return flag_data

    def extract_all(
        self, record: SimpleFastxRecord, match: Match
    ) -> Dict[str, FlagData]:
        flag_data: Dict[str, FlagData] = {}
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

    def update(
        self, record: SimpleFastxRecord, flag_data: Dict[str, FlagData]
    ) -> SimpleFastxRecord:
        name, seq, _ = record
        name_bits = name.split(self._comment_space)
        for name, (flag, start, end) in flag_data.items():
            name_bits[0] += f"{self._flag_delim}{self._flag_delim}{name}"
            name_bits[0] += f"{self._flag_delim}{flag}"
        name = " ".join(name_bits)
        return (name, seq, None)


class FastqFlagExtractor(FastaFlagExtractor):

    extract_qual_flags: bool = True

    def __init__(self, selected_flags: Optional[List[str]] = None):
        super(FastqFlagExtractor, self).__init__(selected_flags)

    def extract_selected(
        self, record: SimpleFastxRecord, match: Match
    ) -> Dict[str, FlagData]:
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        flag_data = super(FastqFlagExtractor, self).extract_selected(record, match)
        if self.extract_qual_flags:
            flag_data = self.__add_qual_flags(flag_data, qual)
        return flag_data

    def extract_all(
        self, record: SimpleFastxRecord, match: Match
    ) -> Dict[str, FlagData]:
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        flag_data = super(FastqFlagExtractor, self).extract_all(record, match)
        if self.extract_qual_flags:
            flag_data = self.__add_qual_flags(flag_data, qual)
        return flag_data

    def __add_qual_flags(
        self, flag_data: Dict[str, FlagData], qual: str
    ) -> Dict[str, FlagData]:
        for name, (_, start, end) in list(flag_data.items()):
            flag = (f"{QFLAG_START}{name}", (qual[slice(start, end)], start, end))
            flag_data.update([flag])
        return flag_data

    def update(
        self, record: SimpleFastxRecord, flag_data: Dict[str, FlagData]
    ) -> SimpleFastxRecord:
        _, _, qual = record
        name, seq, _ = super(FastqFlagExtractor, self).update(record, flag_data)
        return (name, seq, qual)

    def apply_selection(self, flag_data: Dict[str, FlagData]) -> Dict[str, FlagData]:
        if self._selected_flags is None:
            return flag_data
        else:
            selected_flag_data = super(FastqFlagExtractor, self).apply_selection(
                flag_data
            )
            for name in self._selected_flags:
                name = f"{QFLAG_START}{name}"
                if name in flag_data.keys():
                    selected_flag_data[name] = flag_data[name]
            return selected_flag_data


def get_fastx_flag_extractor(fmt: FastxFormats) -> Type[ABCFlagExtractor]:
    """Retrieves appropriate flag extractor class."""
    if FastxFormats.FASTA == fmt:
        return FastaFlagExtractor
    elif FastxFormats.FASTQ == fmt:
        return FastqFlagExtractor
    else:
        return ABCFlagExtractor
