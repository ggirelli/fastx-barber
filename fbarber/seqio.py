'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from Bio import SeqIO
import gzip
import os
from typing import Tuple, Union

FastXParser = Union[
    SeqIO.QualityIO.FastqPhredIterator,
    SeqIO.FastaIO.FastaIterator]


def get_fastx_handler(handle: str) -> Tuple[FastXParser, str]:
    base, ext = os.path.splitext(handle)
    if ".gz" == ext:
        handle = gzip.open(handle, "rt")
        base, ext = os.path.splitext(base)
    assert ext in [".fa", ".fasta", ".fq", ".fastq"], ext
    if ext in [".fa", ".fasta"]:
        handle = SeqIO.parse(handle, "fasta")
        fmt = "fasta"
    elif ext in [".fq", ".fastq"]:
        handle = SeqIO.parse(handle, "fastq")
        fmt = "fastq"
    return (handle, fmt)
