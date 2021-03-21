"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from fastx_barber.const import FastxFormats
from fastx_barber.match import ANPMatch
from fastx_barber.qual import QualityIO
from fastx_barber.seqio import SimpleFastxRecord, SimpleFastqRecord
from typing import Any, List, Match, Tuple, Type, Union


class ABCTrimmer(metaclass=ABCMeta):
    """Record trimmer abstract base class

    Extends:
        metaclass=ABCMeta
    """

    @staticmethod
    @abstractmethod
    def trim_re(record: Any, match: Union[ANPMatch, Match, None]) -> Any:
        """Trim record using regexp match

        Decorators:
            staticmethod
            abstractmethod

        Arguments:
            record {Any} -- record to be trimmed
            match {Match} -- regexp match

        Returns:
            Any -- trimmed record
        """
        pass

    @staticmethod
    @abstractmethod
    def trim_len(record: Any, length: int, side: int) -> Any:
        """Trim record by length

        Decorators:
            staticmethod
            abstractmethod

        Arguments:
            record {Any} -- record to be trimmed
            length {int} -- length to be trimmed
            side {int} -- side to trim (5/3')

        Returns:
            Any -- trimmed record
        """
        pass


class FastaTrimmer(ABCTrimmer):
    def __init__(self):
        super(FastaTrimmer, self).__init__()

    @staticmethod
    def trim_re(
        record: SimpleFastxRecord, match: Union[ANPMatch, Match, None]
    ) -> SimpleFastxRecord:
        assert match is not None
        name, seq, _ = record
        seq = seq[: match.start(0)] + seq[match.end(0) :]
        return (name, seq, None)

    @staticmethod
    def trim_len(
        record: SimpleFastxRecord, length: int, side: int
    ) -> SimpleFastxRecord:
        if 5 == side:
            return (record[0], record[1][length:], None)
        elif 3 == side:
            return (record[0], record[1][:-length], None)
        else:
            raise Exception("Can trim only from 5' or 3' end.")


class FastqTrimmer(ABCTrimmer):
    def __init__(self):
        super(FastqTrimmer, self).__init__()

    @staticmethod
    def trim_re(
        record: SimpleFastxRecord, match: Union[ANPMatch, Match, None]
    ) -> SimpleFastxRecord:
        assert match is not None
        name, seq, qual = record
        assert qual is not None
        seq = seq[: match.start(0)] + seq[match.end(0) :]
        qual = qual[: match.start(0)] + qual[match.end(0) :]
        return (name, seq, qual)

    @staticmethod
    def trim_len(
        record: SimpleFastqRecord, length: int, side: int
    ) -> SimpleFastxRecord:
        if 5 == side:
            return (record[0], record[1][length:], record[2][length:])
        elif 3 == side:
            return (record[0], record[1][:-length], record[2][:-length])
        else:
            raise Exception("Can trim only from 5' or 3' end.")

    @staticmethod
    def __trim_qual_5(
        record: SimpleFastqRecord, qscore_thr: int, bases_qscores: List[int]
    ) -> Tuple[SimpleFastqRecord, int]:
        trimmed_length = 0
        while 0 < len(bases_qscores):
            if bases_qscores[0] < qscore_thr:
                record = (record[0], record[1][1:], record[2][1:])
                bases_qscores = bases_qscores[1:]
                trimmed_length += 1
            else:
                break
        return (record, trimmed_length)

    @staticmethod
    def __trim_qual_3(
        record: SimpleFastqRecord, qscore_thr: int, bases_qscores: List[int]
    ) -> Tuple[SimpleFastqRecord, int]:
        trimmed_length = 0
        while 0 < len(bases_qscores):
            if bases_qscores[-1] < qscore_thr:
                record = (record[0], record[1][:-1], record[2][:-1])
                bases_qscores = bases_qscores[:-1]
                trimmed_length += 1
            else:
                break
        return (record, trimmed_length)

    @staticmethod
    def trim_qual(
        record: SimpleFastqRecord, qscore_thr: int, side: int, qio: QualityIO
    ) -> Tuple[SimpleFastqRecord, int]:
        """Trim record by length

        Decorators:
            staticmethod
            abstractmethod

        Arguments:
            record {SimpleFastqRecord} -- record to be trimmed
            qscore_thr {int} -- qscore threshold, bases with lower qscore are trimmed
            side {int} -- side to trim (5/3')
            qio {QualityIO} -- QualityIO instance for qscore calculation

        Returns:
            SimpleFastqRecord -- trimmed record
        """
        bases_qscores = qio.phred_to_qscore(record[2])
        if 5 == side:
            return FastqTrimmer.__trim_qual_5(record, qscore_thr, bases_qscores)
        elif 3 == side:
            return FastqTrimmer.__trim_qual_3(record, qscore_thr, bases_qscores)
        else:
            raise Exception("Can trim only from 5' or 3' end.")


def get_fastx_trimmer(fmt: FastxFormats) -> Type[ABCTrimmer]:
    """Retrieves appropriate trimmer class."""
    if FastxFormats.FASTA == fmt:
        return FastaTrimmer
    elif FastxFormats.FASTQ == fmt:
        return FastqTrimmer
    else:
        return ABCTrimmer
