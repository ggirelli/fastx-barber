'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from Bio import SeqIO
import gzip
import os
from typing import Tuple, Union

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


def get_fastx_parser(handle: str) -> Tuple[FastXParser, str]:
    fmt, gzipped = get_fastx_format(handle)
    if gzipped:
        handle = gzip.open(handle, "rt")
    if fmt == "fasta":
        handle = SeqIO.FastaIO.SimpleFastaParser(handle)
    elif fmt == "fastq":
        handle = SeqIO.QualityIO.FastqGeneralIterator(handle)
    return (handle, fmt)


class SimpleFastxWriter(object):
    """Simple record writer class for fasta and fastq files"""
    def __init__(self, path: str):
        super(SimpleFastxWriter, self).__init__()
        self.__fmt, gzipped = get_fastx_format(path)
        if gzipped:
            self._OH = gzip.open(path, "wt+")
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
