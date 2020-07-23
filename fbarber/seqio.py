'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from Bio import SeqIO
import gzip
import os
from typing import IO, Tuple, Union

FastaSimpleRecord = Tuple[str, str]
FastqSimpleRecord = Tuple[str, str, str]
FastxSimpleRecord = Union[FastaSimpleRecord, FastqSimpleRecord]

FastXParser = Union[
    SeqIO.QualityIO.FastqGeneralIterator,
    SeqIO.FastaIO.SimpleFastaParser]


def get_fastx_format(path: str) -> Tuple[str, bool]:
    base, ext = os.path.splitext(path)
    gzipped = ".gz" == ext
    if gzipped:
        base, ext = os.path.splitext(base)
    assert ext in [".fa", ".fasta", ".fq", ".fastq"], ext
    if ext in [".fa", ".fasta"]:
        return ("fasta", gzipped)
    elif ext in [".fq", ".fastq"]:
        return ("fastq", gzipped)
    else:
        return ("", False)


def get_fastx_parser(path: str) -> Tuple[FastXParser, str]:
    fmt, gzipped = get_fastx_format(path)
    handle: Union[str, IO] = path
    if gzipped:
        handle = gzip.open(path, "rt")
    if fmt == "fasta":
        parser = SeqIO.FastaIO.SimpleFastaParser(handle)
    elif fmt == "fastq":
        parser = SeqIO.QualityIO.FastqGeneralIterator(handle)
    return (parser, fmt)


class SimpleFastxWriter(object):
    """Simple record writer class for fasta and fastq files"""
    def __init__(self, path: str, compress_level: int = 6):
        super(SimpleFastxWriter, self).__init__()
        self.__fmt, gzipped = get_fastx_format(path)
        if gzipped:
            self._OH = gzip.open(path, "wt+", compress_level)
        else:
            self._OH = open(path, "w+")
        if "fasta" == self.__fmt:
            self.write_record = self._write_fasta_record
        elif "fastq" == self.__fmt:
            self.write_record = self._write_fastq_record

    @property
    def format(self):
        return self.__fmt

    def _write_record(self, record: FastaSimpleRecord) -> None:
        pass

    def _write_fasta_record(self, record: FastaSimpleRecord) -> None:
        self._OH.write(f">{record[0]}\n{record[1]}\n")

    def _write_fastq_record(self, record: FastqSimpleRecord) -> None:
        self._OH.write(f"@{record[0]}\n{record[1]}\n+\n{record[2]}\n")

    def close(self):
        self._OH.close()
