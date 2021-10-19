"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from fastx_barber.const import FastxFormats, FlagData, FlagStatsType, QFLAG_START
from fastx_barber.match import ANPMatch
from fastx_barber.seqio import SimpleFastxRecord
import logging
import os
import pandas as pd  # type: ignore
import regex as re  # type: ignore
from rich.progress import track  # type: ignore
from typing import Any, Dict, List, Match, Optional, Pattern, Tuple, Type, Union


class FlagStats(object):

    __stats: FlagStatsType
    _flags_for_stats: Optional[List[str]] = None

    def __init__(self, flags_for_stats: Optional[List[str]] = None):
        super(FlagStats, self).__init__()
        self.__stats = defaultdict(lambda: defaultdict(lambda: 0))
        self._flags_for_stats = flags_for_stats

    def update(self, flags: Dict[str, FlagData]) -> None:
        if self._flags_for_stats is None:
            return
        for flag_name, flag_data in flags.items():
            if flag_name in self._flags_for_stats:
                self.__stats[flag_name][flag_data[0]] += 1

    def __getitem__(self, key):
        return self.__stats[key]

    def __setitem__(self, key, value):
        self.__stats[key] = value

    def keys(self):
        return self.__stats.keys()

    def values(self):
        return self.__stats.values()

    def items(self):
        return self.__stats.items()

    def get_dataframe(self, flag_name: str) -> pd.DataFrame:
        stats = self.__stats[flag_name]
        df = pd.DataFrame()
        df["value"] = list(stats.keys())
        df["counts"] = list(stats.values())
        df["perc"] = round(df["counts"] / df["counts"].sum() * 100, 2)
        df.sort_values("counts", ascending=False, ignore_index=True, inplace=True)
        return df

    def export(self, output_path: str, verbose: bool = True) -> None:
        output_dir = os.path.dirname(output_path)
        basename = os.path.basename(output_path)
        if basename.endswith(".gz"):
            basename = basename.split(".gz")[0]
        basename = os.path.splitext(basename)[0]
        if verbose:
            flag_keys = track(self.keys(), description="Exporting flagstats")
        else:
            flag_keys = self.keys()

        for flag_name in list(flag_keys):
            self.get_dataframe(flag_name).to_csv(
                os.path.join(output_dir, f"{basename}.{flag_name}.stats.tsv"),
                sep="\t",
                index=False,
            )


class ABCFlagBase(metaclass=ABCMeta):
    """Class with basic flag-related variables

    Extends:
        metaclass=ABCMeta

    Variables:
        _flag_delim {str} -- flag delimiter
        _comment_space {str} -- fastx comment separator
    """

    _flag_delim: str = "~"
    _comment_space: str = " "

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


class ABCFlagExtractor(ABCFlagBase):
    """Flag extractor abstract base class

    Extends:
        ABCFlagBase

    Variables:
        _selected_flags {Optional[List[str]]} -- flags to extract
        _flags_for_stats {Optional[List[str]]} -- list of flags for stats calculation
        _flagstats {FlagStats} -- to contain flagstats generated by update_stats
    """

    _selected_flags: Optional[List[str]] = None
    _flagstats: FlagStats

    def __init__(
        self,
        selected_flags: Optional[List[str]] = None,
        flags_for_stats: Optional[List[str]] = None,
    ):
        self._selected_flags = selected_flags
        self._flagstats = FlagStats(flags_for_stats)

    @property
    def flagstats(self):
        return self._flagstats

    @abstractmethod
    def extract_selected(
        self, record: Any, match: Union[ANPMatch, Match, None]
    ) -> Dict[str, FlagData]:
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
    def extract_all(
        self, record: Any, match: Union[ANPMatch, Match, None]
    ) -> Dict[str, FlagData]:
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

    def update_stats(self, flags: Dict[str, FlagData]) -> None:
        self._flagstats.update(flags)

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
        return {
            name: flag_data[name] for name in self._selected_flags if name in flag_data
        }


class FastaFlagExtractor(ABCFlagExtractor):
    def extract_selected(
        self, record: SimpleFastxRecord, match: Union[ANPMatch, Match, None]
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
        self, record: SimpleFastxRecord, match: Union[ANPMatch, Match, None]
    ) -> Dict[str, FlagData]:
        if match is None:
            return {}
        flag_data: Dict[str, FlagData] = {}
        for gid in range(len(match.groups())):
            flag = self.__extract_single_flag(match, gid)
            flag_data.update([flag])
        return flag_data

    def __extract_single_flag(
        self,
        match: Union[ANPMatch, Match],
        gid: int,
        flag: Optional[Tuple[str, str]] = None,
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

    def extract_selected(
        self, record: SimpleFastxRecord, match: Union[ANPMatch, Match, None]
    ) -> Dict[str, FlagData]:
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        flag_data = super(FastqFlagExtractor, self).extract_selected(record, match)
        if self.extract_qual_flags:
            flag_data = self.__add_qual_flags(flag_data, qual)
        return flag_data

    def extract_all(
        self, record: SimpleFastxRecord, match: Union[ANPMatch, Match, None]
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
        selected_flag_data = super(FastqFlagExtractor, self).apply_selection(flag_data)
        for name in self._selected_flags:
            name = f"{QFLAG_START}{name}"
            if name in flag_data:
                selected_flag_data[name] = flag_data[name]
        return selected_flag_data


def get_fastx_flag_extractor(fmt: FastxFormats) -> Type[ABCFlagExtractor]:
    """Retrieves appropriate flag extractor class."""
    if FastxFormats.FASTA == fmt:
        return FastaFlagExtractor
    if FastxFormats.FASTQ == fmt:
        return FastqFlagExtractor
    return ABCFlagExtractor


class ABCFlagReader(ABCFlagBase):
    @abstractmethod
    def read(self, record: Any) -> Optional[Dict[str, FlagData]]:
        pass


class FastxFlagReader(ABCFlagReader):

    _flagstats: FlagStats

    def __init__(self, flags_for_stats: Optional[List[str]] = None):
        super(FastxFlagReader, self).__init__()
        self._flagstats = FlagStats(flags_for_stats)

    @property
    def flagstats(self):
        return self._flagstats

    def read(self, record: SimpleFastxRecord) -> Optional[Dict[str, FlagData]]:
        header = record[0]
        if self._comment_space in header:
            header = header.split(self._comment_space)[0]
        double_delim = f"{self._flag_delim}{self._flag_delim}"
        if double_delim not in header:
            return None
        flag_data: Dict[str, FlagData] = {}
        for flag in header.split(double_delim)[1:]:
            if self._flag_delim not in flag:
                continue
            name, value = flag.split(self._flag_delim)[:2]
            flag_data.update([(name, (value, -1, -1))])
        self._flagstats.update(flag_data)
        return flag_data


class FlagRegexes(object):

    _flag_regex: Dict[str, str]
    _flag_regex_compiled: Dict[str, Pattern]

    def __init__(self, pattern_list: List[str]):
        super(FlagRegexes, self).__init__()
        self._flag_regex = {}
        self.__init(pattern_list)
        self._flag_regex_compiled = {}
        self.__compile()

    def __init(self, pattern_list: List[str]) -> Dict[str, str]:
        self._flag_regex = {}
        for pattern in pattern_list:
            if "," not in pattern:
                continue
            exploded = pattern.split(",")
            self._flag_regex[exploded[0]] = ",".join(exploded[1:])
        return self._flag_regex

    def __compile(self) -> None:
        for name, regex in self._flag_regex.items():
            self._flag_regex_compiled[name] = re.compile(regex)

    def log(self) -> None:
        logging.info("[bold underline red]Flag regex[/]")
        for name, regex in self._flag_regex.items():
            logging.info(f"{name}-regex\t{regex}")

    def match(self, flags: Dict[str, FlagData]) -> bool:
        for name, regex in self._flag_regex_compiled.items():
            if name not in flags:
                return False
            match = re.match(regex, flags[name][0])
            if match is None:
                return False
        return True
