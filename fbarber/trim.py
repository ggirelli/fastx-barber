'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from abc import ABCMeta, abstractmethod
from fbarber.const import FastxFormats
from fbarber.seqio import FastxSimpleRecord
import regex  # type: ignore
from typing import Any, Match, Type


class ABCTrimmer(metaclass=ABCMeta):
    """Record matcher abstract base class"""

    @staticmethod
    @abstractmethod
    def trim_re(record: Any, match: Match
                ) -> Any: pass


class FastaTrimmer(ABCTrimmer):
    """Fasta record trimmer class"""

    def __init__(self):
        super(FastaTrimmer, self).__init__()

    @staticmethod
    def trim_re(record: FastxSimpleRecord, match: Match
                ) -> FastxSimpleRecord:
        assert match is not None
        name, seq, _ = record
        seq = regex.sub(match.re, "", seq)
        return (name, seq, None)


class FastqTrimmer(FastaTrimmer):
    """Fastq record trimmer class"""

    def __init__(self):
        super(FastqTrimmer, self).__init__()

    @staticmethod
    def trim_re(record: FastxSimpleRecord, match: Match
                ) -> FastxSimpleRecord:
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        seq = regex.sub(match.re, "", seq)
        qual = qual[-len(seq):]
        return (name, seq, qual)


def get_fastx_trimmer(fmt: FastxFormats) -> Type[ABCTrimmer]:
    if FastxFormats.FASTA == fmt:
        return FastaTrimmer
    elif FastxFormats.FASTQ == fmt:
        return FastqTrimmer
    else:
        return ABCTrimmer
