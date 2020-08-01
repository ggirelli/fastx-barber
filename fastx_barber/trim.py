"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from fastx_barber.const import FastxFormats
from fastx_barber.seqio import FastxSimpleRecord
import regex  # type: ignore
from typing import Any, Match, Type


class ABCTrimmer(metaclass=ABCMeta):
    """Record trimmer abstract base class

    Extends:
        metaclass=ABCMeta
    """

    @staticmethod
    @abstractmethod
    def trim_re(record: Any, match: Match) -> Any:
        """Trim record using regexp match

        Decorators:
            staticmethod
            abstractmethod

        Arguments:
            record {Any} -- record to be trimmed
            match {Match} -- regexp match
        """
        pass


class FastaTrimmer(ABCTrimmer):
    """Fasta record trimmer class"""

    def __init__(self):
        super(FastaTrimmer, self).__init__()

    @staticmethod
    def trim_re(record: FastxSimpleRecord, match: Match) -> FastxSimpleRecord:
        """Trim fasta record using regexp match

        Decorators:
            staticmethod

        Arguments:
            record {Any} -- record to be trimmed
            match {Match} -- regexp match
        """
        assert match is not None
        name, seq, _ = record
        seq = regex.sub(match.re, "", seq)
        return (name, seq, None)


class FastqTrimmer(FastaTrimmer):
    """Fastq record trimmer class"""

    def __init__(self):
        super(FastqTrimmer, self).__init__()

    @staticmethod
    def trim_re(record: FastxSimpleRecord, match: Match) -> FastxSimpleRecord:
        """Trim fastq record using regexp match

        Decorators:
            staticmethod

        Arguments:
            record {Any} -- record to be trimmed
            match {Match} -- regexp match
        """
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        seq = regex.sub(match.re, "", seq)
        qual = qual[-len(seq) :]
        return (name, seq, qual)


def get_fastx_trimmer(fmt: FastxFormats) -> Type[ABCTrimmer]:
    """Retrieves appropriate trimmer class.

    Arguments:
        fmt {FastxFormats}

    Returns:
        Type[ABCTrimmer] -- trimmer class
    """
    if FastxFormats.FASTA == fmt:
        return FastaTrimmer
    elif FastxFormats.FASTQ == fmt:
        return FastqTrimmer
    else:
        return ABCTrimmer
