'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from Bio import SeqIO
import gzip
import os
from typing import Tuple, Union

FastXParser = Union[
    SeqIO.QualityIO.FastqGeneralIterator,
    SeqIO.FastaIO.SimpleFastaParser]


def get_fastx_handler(handle: str) -> Tuple[FastXParser, str]:
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
