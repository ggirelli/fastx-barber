'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from abc import ABCMeta, abstractmethod
from fbarber.seqio import FastxSimpleRecord
from fbarber.const import FastxFormats
from typing import Any, Dict, Match, Type


class ABCFlagExtractor(metaclass=ABCMeta):
    """Flag extractor abstract base class

    Extends:
        metaclass=ABCMeta

    Variables:
        _delim {str} -- flag delimiter
        _comment_space {str} -- fastx comment separator
    """

    _delim: str
    _comment_space: str

    def __init__(self,
                 flag_delim: str = "~",
                 comment_space: str = " "):
        """Initialize flag extractor

        Keyword Arguments:
            flag_delim {str} -- flag delimiter (default: {"~"})
            comment_space {str} -- fastx comment separator (default: {" "})
        """
        assert 1 == len(flag_delim)
        self._delim = flag_delim
        assert 1 == len(comment_space)
        self._comment_space = comment_space

    @abstractmethod
    def extract(self, record: Any, match: Match) -> Dict[str, str]:
        """Extract flags

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

    def __init__(self,
                 flag_delim: str = "~",
                 comment_space: str = " "):
        """Initialize fasta file flag extractor

        Keyword Arguments:
            flag_delim {str} -- flag delimiter (default: {"~"})
            comment_space {str} -- fasta comment separator (default: {" "})
        """
        super(FastaFlagExtractor, self).__init__(
            flag_delim, comment_space)

    def extract(self, record: FastxSimpleRecord, match: Match
                ) -> Dict[str, str]:
        """Extract flags

        Arguments:
            record {FastxSimpleRecord} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        assert match is not None
        return match.groupdict()

    def update(self, record: FastxSimpleRecord, match: Match
               ) -> FastxSimpleRecord:
        """Update record

        Arguments:
            name {str} -- record to update based on flags
            match {Match} -- results of matching the record to a flag pattern
        """
        name, seq, _ = record
        name_bits = name.split(self._comment_space)
        for label, value in self.extract(record, match).items():
            name_bits[0] += f"{self._delim}{self._delim}{label}"
            name_bits[0] += f"{self._delim}{value}"
        name = " ".join(name_bits)
        return (name, seq, None)


class FastqFlagExtractor(FastaFlagExtractor):
    """Fastq flag extractor class"""

    def __init__(self,
                 flag_delim: str = "~",
                 comment_space: str = " "):
        """Initialize fastq file flag extractor

        Keyword Arguments:
            flag_delim {str} -- flag delimiter (default: {"~"})
            comment_space {str} -- fastq comment separator (default: {" "})
        """
        super(FastqFlagExtractor, self).__init__(
            flag_delim, comment_space)

    def extract(self, record: FastxSimpleRecord, match: Match
                ) -> Dict[str, str]:
        """Extract flags

        Arguments:
            record {FastxSimpleRecord} -- record from where to extract flags
            match {Match} -- results of matching the record to a flag pattern
        """
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        flags = super(FastqFlagExtractor, self).extract(record, match)
        flag_names = list(match.groupdict().keys())
        for gid in range(len(match.groups())):
            group_slice = slice(match.start(gid + 1), match.end(gid + 1))
            flags[f"q{flag_names[gid]}"] = qual[group_slice]
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
