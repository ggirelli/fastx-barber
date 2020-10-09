"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.const import FastxFormats
from fastx_barber import io, random, seqio
import os
import shutil
import tempfile


def test_get_fastx_format():
    assert (FastxFormats.FASTA, True) == seqio.get_fastx_format("fake.fasta.gz")
    assert (FastxFormats.FASTA, False) == seqio.get_fastx_format("fake.fasta")
    assert (FastxFormats.FASTQ, True) == seqio.get_fastx_format("fake.fastq.gz")
    assert (FastxFormats.FASTQ, False) == seqio.get_fastx_format("fake.fastq")
    assert (FastxFormats.FASTA, True) == seqio.get_fastx_format("fake.fa.gz")
    assert (FastxFormats.FASTA, False) == seqio.get_fastx_format("fake.fa")
    assert (FastxFormats.FASTQ, True) == seqio.get_fastx_format("fake.fq.gz")
    assert (FastxFormats.FASTQ, False) == seqio.get_fastx_format("fake.fq")
    try:
        seqio.get_fastx_format("fake.txt.gz")
    except AssertionError:
        pass
    try:
        seqio.get_fastx_format("fake.txt")
    except AssertionError:
        pass


def test_get_fastx_parser():
    fapath, dpath = random.write_tmp_fastx_file(FastxFormats.FASTA, 30, 100)
    for record in seqio.get_fastx_parser(fapath)[0]:
        pass
    fqpath, _ = random.write_tmp_fastx_file(FastxFormats.FASTA, 30, 100, dpath)
    for record in seqio.get_fastx_parser(fqpath)[0]:
        pass
    zfapath, _ = random.write_tmp_fastx_file(
        FastxFormats.FASTA, 30, 100, dpath, gzipped=True
    )
    for record in seqio.get_fastx_parser(zfapath)[0]:
        pass
    zfqpath, _ = random.write_tmp_fastx_file(
        FastxFormats.FASTA, 30, 100, dpath, gzipped=True
    )
    for record in seqio.get_fastx_parser(zfqpath)[0]:
        pass
    shutil.rmtree(dpath)


def test_FastxChunkedParser():
    fapath, dpath = random.write_tmp_fastx_file(FastxFormats.FASTA, 30, 100)
    fachunks = [
        c for c in seqio.FastxChunkedParser(seqio.get_fastx_parser(fapath)[0], 8)
    ]
    assert 4 == len(fachunks)
    fqpath, _ = random.write_tmp_fastx_file(FastxFormats.FASTA, 30, 100, dpath)
    fqchunks = [
        c for c in seqio.FastxChunkedParser(seqio.get_fastx_parser(fqpath)[0], 8)
    ]
    assert 4 == len(fqchunks)
    zfapath, _ = random.write_tmp_fastx_file(
        FastxFormats.FASTA, 30, 100, dpath, gzipped=True
    )
    fachunks = [
        c for c in seqio.FastxChunkedParser(seqio.get_fastx_parser(zfapath)[0], 8)
    ]
    assert 4 == len(fachunks)
    zfqpath, _ = random.write_tmp_fastx_file(
        FastxFormats.FASTA, 30, 100, dpath, gzipped=True
    )
    fqchunks = [
        c for c in seqio.FastxChunkedParser(seqio.get_fastx_parser(zfqpath)[0], 8)
    ]
    assert 4 == len(fqchunks)
    shutil.rmtree(dpath)


def test_SimpleFastaWriter():
    tmp_dir = io.check_tmp_dir()
    generated_records = random.make_fasta_file(100, 200)
    _, fpath = tempfile.mkstemp(
        dir=tmp_dir, suffix=random.mk_suffix(FastxFormats.FASTA, False), text=True
    )
    OH = seqio.SimpleFastaWriter(fpath)
    for record in generated_records:
        OH.write(record)
    OH.close()
    written_records = [r for r in seqio.get_fastx_parser(fpath)[0]]
    for i in range(len(generated_records)):
        assert generated_records[i] == written_records[i]
    shutil.rmtree(tmp_dir)


def test_SimpleFastqWriter():
    tmp_dir = io.check_tmp_dir()
    generated_records = random.make_fastq_file(100, 200)
    _, fpath = tempfile.mkstemp(
        dir=tmp_dir, suffix=random.mk_suffix(FastxFormats.FASTQ, False), text=True
    )
    OH = seqio.SimpleFastqWriter(fpath)
    for record in generated_records:
        OH.write(record)
    OH.close()
    written_records = [r for r in seqio.get_fastx_parser(fpath)[0]]
    for i in range(len(generated_records)):
        assert generated_records[i] == written_records[i]
    shutil.rmtree(tmp_dir)


def test_get_fastx_writer():
    assert seqio.get_fastx_writer(FastxFormats.FASTA) is seqio.SimpleFastaWriter
    assert seqio.get_fastx_writer(FastxFormats.FASTQ) is seqio.SimpleFastqWriter
    assert seqio.get_fastx_writer(FastxFormats.NONE) is seqio.SimpleFastxWriter


def test_SimpleSplitFastaWriter():
    tmp_dir = io.check_tmp_dir()
    generated_records = random.make_fasta_file(100, 200)
    _, fpath = tempfile.mkstemp(
        dir=tmp_dir, suffix=random.mk_suffix(FastxFormats.FASTA, False), text=True
    )
    OH = seqio.SimpleSplitFastaWriter(fpath, "first")
    for record in generated_records:
        OH.write(record, {"first": (record[1][0], 0, 0)})
    for c in random.DNA_ALPHABET:
        parser, _ = seqio.get_fastx_parser(
            os.path.join(tmp_dir, f"first_split.{c}.{os.path.basename(fpath)}")
        )
        for record in parser:
            assert c == record[1][0]
    shutil.rmtree(tmp_dir)


def test_SimpleSplitFastqWriter():
    tmp_dir = io.check_tmp_dir()
    generated_records = random.make_fastq_file(100, 200)
    _, fpath = tempfile.mkstemp(
        dir=tmp_dir, suffix=random.mk_suffix(FastxFormats.FASTQ, False), text=True
    )
    OH = seqio.SimpleSplitFastqWriter(fpath, "first")
    for record in generated_records:
        OH.write(record, {"first": (record[1][0], 0, 0)})
    for c in random.DNA_ALPHABET:
        parser, _ = seqio.get_fastx_parser(
            os.path.join(tmp_dir, f"first_split.{c}.{os.path.basename(fpath)}")
        )
        for record in parser:
            assert c == record[1][0]
    shutil.rmtree(tmp_dir)


def test_get_split_fastx_writer():
    assert (
        seqio.get_split_fastx_writer(FastxFormats.FASTA) is seqio.SimpleSplitFastaWriter
    )
    assert (
        seqio.get_split_fastx_writer(FastxFormats.FASTQ) is seqio.SimpleSplitFastqWriter
    )
    assert (
        seqio.get_split_fastx_writer(FastxFormats.NONE) is seqio.SimpleSplitFastxWriter
    )
