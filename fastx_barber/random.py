"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.const import FastxFormats
from fastx_barber.io import check_tmp_dir
from fastx_barber.seqio import (
    SimpleFastaRecord,
    SimpleFastaWriter,
    SimpleFastqRecord,
    SimpleFastqWriter,
)
from random import choice
import tempfile
from typing import List, Optional, Tuple

DNA_ALPHABET: List[str] = ["A", "T", "C", "G"]
QUAL_ALPHABET: List[str] = list("!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJ")


def make_random_string(length: int, alphabet: List[str] = DNA_ALPHABET) -> str:
    return "".join([choice(alphabet) for i in range(length)])


def make_fasta_record(name: str, length: int) -> SimpleFastaRecord:
    return (name, make_random_string(length), None)


def make_fasta_file(n_records: int, seq_length: int) -> List[SimpleFastaRecord]:
    records: List[SimpleFastaRecord] = []
    for i in range(n_records):
        records.append(make_fasta_record(f"record_{i+1}", seq_length))
    return records


def make_fastq_record(name: str, length: int) -> SimpleFastqRecord:
    return (
        *make_fasta_record(name, length)[:2],
        make_random_string(length, QUAL_ALPHABET),
    )


def make_fastq_file(n_records: int, seq_length: int) -> List[SimpleFastqRecord]:
    records: List[SimpleFastqRecord] = []
    for i in range(n_records):
        records.append(make_fastq_record(f"record_{i+1}", seq_length))
    return records


def mk_suffix(fmt: FastxFormats, gzipped):
    if fmt is FastxFormats.FASTA:
        suffix = ".fasta"
    else:
        suffix = ".fastq"
    if gzipped:
        suffix += ".gz"
    return suffix


def write_tmp_fasta_file(
    n_records: int,
    seq_length: int,
    tmp_dir: Optional[str] = None,
    gzipped: bool = False,
    compresslevel: int = 6,
) -> Tuple[str, str]:
    """Temporary FASTA file is not automatically deleted."""
    tmp_dir = check_tmp_dir(tmp_dir)
    generated_records = make_fasta_file(n_records, seq_length)
    _, tmp_fpath = tempfile.mkstemp(
        dir=tmp_dir, suffix=mk_suffix(FastxFormats.FASTA, gzipped), text=True
    )
    OH = SimpleFastaWriter(tmp_fpath)
    for record in generated_records:
        OH.write(record)
    return (tmp_fpath, tmp_dir)


def write_tmp_fastq_file(
    n_records: int,
    seq_length: int,
    tmp_dir: Optional[str] = None,
    gzipped: bool = False,
    compresslevel: int = 6,
) -> Tuple[str, str]:
    """Temporary FASTQ file is not automatically deleted."""
    tmp_dir = check_tmp_dir(tmp_dir)
    generated_records = make_fastq_file(n_records, seq_length)
    _, tmp_fpath = tempfile.mkstemp(
        dir=tmp_dir, suffix=mk_suffix(FastxFormats.FASTQ, gzipped), text=True
    )
    OH = SimpleFastqWriter(tmp_fpath)
    for record in generated_records:
        OH.write(record)
    return (tmp_fpath, tmp_dir)


def write_tmp_fastx_file(
    fmt: FastxFormats,
    n_records: int,
    seq_length: int,
    tmp_dir: Optional[str] = None,
    gzipped: bool = False,
    compresslevel: int = 6,
) -> Tuple[str, str]:
    """Temporary FASTX file is not automatically deleted."""
    if fmt is FastxFormats.FASTA:
        return write_tmp_fasta_file(
            n_records, seq_length, tmp_dir, gzipped, compresslevel
        )
    if fmt is FastxFormats.FASTQ:
        return write_tmp_fastq_file(
            n_records, seq_length, tmp_dir, gzipped, compresslevel
        )
    assert fmt is not FastxFormats.NONE
