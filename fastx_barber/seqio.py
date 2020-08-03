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
from typing import Any, IO, Iterator, List, Optional, Tuple, Type, Union

SimpleFastxRecord = Tuple[str, str, Optional[str]]

SimpleFastxParser = Union[
    SeqIO.QualityIO.FastqGeneralIterator, SeqIO.FastaIO.SimpleFastaParser
]


def get_fastx_format(path: str) -> Tuple[FastxFormats, bool]:
    """
    Returns:
        Tuple[FastxFormats, bool] -- fastx file format and gzipped status
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


def get_fastx_parser(path: str) -> Tuple[SimpleFastxParser, FastxFormats]:
    """Retrieves appropriate simple parser and associated format (fasta or fastq)."""
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


class FastxChunkedParser(object):
    """Parser with chunking capabilities for fasta and fastq files.

    Variables:
        __IH: SimpleFastxParser {[type]} -- [description]
    """

    __IH: SimpleFastxParser
    __chunk_size: int
    __chunk_counter: int = 0

    def __init__(self, parser: SimpleFastxParser, chunk_size: int):
        super(FastxChunkedParser, self).__init__()
        self.__IH = parser
        assert chunk_size > 0
        self.__chunk_size = chunk_size

    @property
    def chunk_size(self):
        return self.__chunk_size

    @property
    def last_chunk_id(self):
        return self.__chunk_counter

    def __next__(self) -> Tuple[List[SimpleFastxRecord], int]:
        chunk: List[SimpleFastxRecord] = []
        while len(chunk) < self.__chunk_size:
            try:
                chunk.append(next(self.__IH))
            except StopIteration:
                break
        if 0 == len(chunk):
            raise StopIteration
        else:
            self.__chunk_counter += 1
            return (chunk, self.__chunk_counter)

    def __iter__(self) -> Iterator[Tuple[List[SimpleFastxRecord], int]]:
        return self


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

    @property
    def name(self) -> str:
        return self._OH.name

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

    _fmt: FastxFormats

    def __init__(self, path: str, compress_level: int = 6):
        super(SimpleFastxWriter, self).__init__(path, compress_level)
        self._fmt, _ = get_fastx_format(path)
        assert self._fmt in FastxFormats

    @property
    def format(self) -> FastxFormats:
        return self._fmt

    @abstractmethod
    def write(self, record: SimpleFastxRecord) -> None:
        """Write record to output buffer

        Decorators:
            abstractmethod

        Arguments:
            record {SimpleFastxRecord} -- record to be written
        """
        pass


class SimpleFastaWriter(SimpleFastxWriter):
    def __init__(self, path: str, compress_level: int = 6):
        super(SimpleFastaWriter, self).__init__(path, compress_level)
        assert FastxFormats.FASTA == self.format

    def write(self, record: SimpleFastxRecord) -> None:
        self._OH.write(f">{record[0]}\n{record[1]}\n")


class SimpleFastqWriter(SimpleFastxWriter):
    def __init__(self, path: str, compress_level: int = 6):
        super(SimpleFastqWriter, self).__init__(path, compress_level)
        assert FastxFormats.FASTQ == self.format

    def write(self, record: SimpleFastxRecord) -> None:
        self._OH.write(f"@{record[0]}\n{record[1]}\n+\n{record[2]}\n")


def get_fastx_writer(fmt: FastxFormats) -> Type[SimpleFastxWriter]:
    """Retrieves appropriate simple writer class."""
    if FastxFormats.FASTA == fmt:
        return SimpleFastaWriter
    elif FastxFormats.FASTQ == fmt:
        return SimpleFastqWriter
    return SimpleFastxWriter
