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


def get_fastx_input_handler(handle: str) -> Tuple[FastXParser, str]:
    base, ext = os.path.splitext(handle)
    if ".gz" == ext:
        handle = gzip.open(handle, "rt")
        base, ext = os.path.splitext(base)
    assert ext in [".fa", ".fasta", ".fq", ".fastq"], ext
    if ext in [".fa", ".fasta"]:
        handle = SeqIO.FastaIO.SimpleFastaParser(handle)
        fmt = "fasta"
    elif ext in [".fq", ".fastq"]:
        handle = SeqIO.QualityIO.FastqGeneralIterator(handle)
        fmt = "fastq"
    return (handle, fmt)


def write_simple_fasta_record(record: FastaSimpleRecord) -> None:
    print("writing fasta")


def write_simple_fastq_record(record: FastqSimpleRecord) -> None:
    print("writing fastq")


def write_simple_fastx_record(record: FastxSimpleRecord) -> None:
    try:
        check_type("record", record, FastaSimpleRecord)
    except TypeError:
        pass
    else:
        write_simple_fasta_record(record)
        return
    try:
        check_type("record", record, FastqSimpleRecord)
    except TypeError:
        raise
    else:
        write_simple_fastq_record(record)
        return
