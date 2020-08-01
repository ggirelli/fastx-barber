"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from abc import ABCMeta, abstractmethod
from Bio import SeqIO  # type: ignore
from fastx_barber.io import is_gzipped
from fastx_barber.const import FastxFormats, FastxExtensions
import gzip
import os
from typing import Any, IO, Optional, Tuple, Type, Union

FastxSimpleRecord = Tuple[str, str, Optional[str]]

FastXParser = Union[
    SeqIO.QualityIO.FastqGeneralIterator, SeqIO.FastaIO.SimpleFastaParser
]


def get_fastx_format(path: str) -> Tuple[FastxFormats, bool]:
    """Identify fastx file format (fasta or fastq).

    Retrieves fastx file format and gzipped status.

    Arguments:
        path {str} -- path to fastx file
    """
    base, ext, gzipped = is_gzipped(path)
    if gzipped:
        base, ext = os.path.splitext(base)
    assert FastxExtensions.has_value(ext), ext
    if ext in FastxExtensions.FASTA.value:
        return (FastxFormats.FASTA, gzipped)
    elif ext in FastxExtensions.FASTQ.value:
        return (FastxFormats.FASTQ, gzipped)
    else:
        return (FastxFormats.NONE, False)


def get_fastx_parser(path: str) -> Tuple[FastXParser, FastxFormats]:
    """Get parser for fasta or fastq file.

    Retrieves appropriate simple parser and associated format (fasta or fastq).

    Arguments:
        path {str} -- path to fastx file
    """
    fmt, gzipped = get_fastx_format(path)
    handle: Union[str, IO] = path
    if gzipped:
        handle = gzip.open(path, "rt")
    assert fmt in FastxFormats
    if FastxFormats.FASTA == fmt:
        parser = SeqIO.FastaIO.SimpleFastaParser(handle)
        parser = ((*x, None) for x in parser)
    elif FastxFormats.FASTQ == fmt:
        parser = SeqIO.QualityIO.FastqGeneralIterator(handle)
    else:
        parser = (x for x in handle)
    return (parser, fmt)


class ABCSimpleWriter(metaclass=ABCMeta):
    """Simple record writer abstract base class

    Extends:
        metaclass=ABCMeta

    Variables:
        _OH {IO} -- output buffer handle
    """

    _OH: IO

    def __init__(self, path: str, compress_level: int = 6):
        """Initialize simple writer

        Arguments:
            path {str} -- path to output file

        Keyword Arguments:
            compress_level {int} -- gzip compression level (default: {6})
        """
        super(ABCSimpleWriter, self).__init__()
        _, _, gzipped = is_gzipped(path)
        if gzipped:
            self._OH = gzip.open(path, "wt+", compress_level)
        else:
            self._OH = open(path, "w+")

    @abstractmethod
    def write(self, record: Any) -> None:
        """Write record to output buffer

        Decorators:
            abstractmethod

        Arguments:
            record {Any} -- record to be written
        """
        pass

    def close(self):
        """Close output buffer handle"""
        self._OH.close()


class SimpleFastxWriter(ABCSimpleWriter):
    """Simple record writer for fasta and fastq files abstract base class

    Extends:
        ABCSimpleWriter

    Variables:
        _fmt {FastxFormats}
    """

    _fmt: FastxFormats

    def __init__(self, path: str, compress_level: int = 6):
        """Initialize fastx simple writer

        Identify fastx file format (fasta or fastq).

        Arguments:
            path {str} -- path to output file

        Keyword Arguments:
            compress_level {int} -- gzip compression level (default: {6})
        """
        super(SimpleFastxWriter, self).__init__(path, compress_level)
        self._fmt, _ = get_fastx_format(path)
        assert self._fmt in FastxFormats

    @property
    def format(self) -> FastxFormats:
        """Fastx file format

        Returns:
            FastxFormats
        """
        return self._fmt

    @abstractmethod
    def write(self, record: FastxSimpleRecord) -> None:
        """Write record to output buffer

        Decorators:
            abstractmethod

        Arguments:
            record {FastxSimpleRecord} -- record to be written
        """
        pass


class SimpleFastaWriter(SimpleFastxWriter):
    """Simple record writer class for fasta files

    Extends:
        SimpleFastxWriter
    """

    def __init__(self, path: str, compress_level: int = 6):
        """Initialize fasta simple writer

        Checks that the input file extension matches the expected one (fasta).

        Arguments:
            path {str} -- path to output file

        Keyword Arguments:
            compress_level {int} -- gzip compression level (default: {6})
        """
        super(SimpleFastaWriter, self).__init__(path, compress_level)
        assert FastxFormats.FASTA == self.format

    def write(self, record: FastxSimpleRecord) -> None:
        """Write fasta record to output buffer

        Arguments:
            record {FastxSimpleRecord} -- fasta record to be written
        """
        self._OH.write(f">{record[0]}\n{record[1]}\n")


class SimpleFastqWriter(SimpleFastxWriter):
    """Simple record writer class for fastq files

    Extends:
        SimpleFastxWriter
    """

    def __init__(self, path: str, compress_level: int = 6):
        """Initialize fastq simple writer

        Checks that the input file extension matches the expected one (fasta).

        Arguments:
            path {str} -- path to output file

        Keyword Arguments:
            compress_level {int} -- gzip compression level (default: {6})
        """
        super(SimpleFastqWriter, self).__init__(path, compress_level)
        assert FastxFormats.FASTQ == self.format

    def write(self, record: FastxSimpleRecord) -> None:
        """Write fastq record to output buffer

        Arguments:
            record {FastxSimpleRecord} -- fastq record to be written
        """
        self._OH.write(f"@{record[0]}\n{record[1]}\n+\n{record[2]}\n")


def get_fastx_writer(fmt: FastxFormats) -> Type[SimpleFastxWriter]:
    """Get writer for fastq or fastq file.

    Retrieves appropriate simple writer class.

    Arguments:
        fmt {FastxFormats}

    Returns:
        Type[SimpleFastxWriter] -- simple writer class
    """
    if FastxFormats.FASTA == fmt:
        return SimpleFastaWriter
    elif FastxFormats.FASTQ == fmt:
        return SimpleFastqWriter
    return SimpleFastxWriter
