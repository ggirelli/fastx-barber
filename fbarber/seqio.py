'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from Bio import SeqIO
import gzip
import os
from typing import Tuple, Union
from typeguard import check_type

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
    """docstring for SimpleFastxWriter"""
    def __init__(self, path: str):
        super(SimpleFastxWriter, self).__init__()
        self.__fmt, gzipped = get_fastx_format(path)
        if gzipped:
            self._OH = gzip.open(path, "wt+")
        else:
            self._OH = open(path, "w+")

    @property
    def format(self):
        return self.__fmt

    def write_fasta_record(self, record: FastaSimpleRecord) -> None:
        self._OH.write(f">{record[0]}\n{record[1]}\n")

    def write_fastq_record(self, record: FastqSimpleRecord) -> None:
        self._OH.write(f"@{record[0]}\n{record[1]}\n+\n{record[2]}\n")

    def write_record(self, record: FastxSimpleRecord) -> None:
        try:
            check_type("record", record, FastaSimpleRecord)
        except TypeError:
            pass
        else:
            self.write_fasta_record(record)
            return
        try:
            check_type("record", record, FastqSimpleRecord)
        except TypeError:
            raise
        else:
            self.write_fastq_record(record)
            return

    def close(self):
        self._OH.close()
