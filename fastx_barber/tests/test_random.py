"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import const, random, seqio
import shutil

TEST_ALPHABET = list("abcde")


def test_make_random_string():
    random_string = random.make_random_string(const.UT_RECORD_SEQ_LEN, TEST_ALPHABET)
    if const.UT_RECORD_SEQ_LEN != len(random_string):
        raise AssertionError
    if not all(c in TEST_ALPHABET for c in random_string):
        raise AssertionError


def assert_fasta_record(
    record: seqio.SimpleFastaRecord, expected_name: str = const.UT_FLAG_NAME
) -> None:
    if not isinstance(record, tuple):
        raise AssertionError
    if not isinstance(record[0], str):
        raise AssertionError
    if 3 != len(record):
        raise AssertionError
    if expected_name != record[0]:
        raise AssertionError
    if not isinstance(record[1], str):
        raise AssertionError
    if const.UT_RECORD_SEQ_LEN != len(record[1]):
        raise AssertionError
    if not all(c in random.DNA_ALPHABET for c in record[1]):
        raise AssertionError
    if record[2] is not None:
        raise AssertionError


def test_make_fasta_record():
    assert_fasta_record(
        random.make_fasta_record(const.UT_FLAG_NAME, const.UT_RECORD_SEQ_LEN)
    )


def test_make_fasta_file():
    fastq = random.make_fasta_file(const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN)
    for i in range(len(fastq)):
        assert_fasta_record(fastq[i], f"record_{i+1}")


def assert_fastq_record(
    record: seqio.SimpleFastqRecord, expected_name: str = const.UT_FLAG_NAME
) -> None:
    if not isinstance(record, tuple):
        raise AssertionError
    if not isinstance(record[0], str):
        raise AssertionError
    if 3 != len(record):
        raise AssertionError
    if expected_name != record[0]:
        raise AssertionError
    if not isinstance(record[1], str):
        raise AssertionError
    if const.UT_RECORD_SEQ_LEN != len(record[1]):
        raise AssertionError
    if not all(c in random.DNA_ALPHABET for c in record[1]):
        raise AssertionError
    if not isinstance(record[2], str):
        raise AssertionError
    if const.UT_RECORD_SEQ_LEN != len(record[2]):
        raise AssertionError
    if not all(c in random.QUAL_ALPHABET for c in record[2]):
        raise AssertionError


def test_make_fastq_record():
    assert_fastq_record(
        random.make_fastq_record(const.UT_FLAG_NAME, const.UT_RECORD_SEQ_LEN)
    )


def test_make_fastq_file():
    fastq = random.make_fastq_file(const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN)
    for i in range(len(fastq)):
        assert_fastq_record(fastq[i], f"record_{i+1}")


def assert_fastx_file(path: str, expected_fmt: const.FastxFormats) -> None:
    parser, fmt = seqio.get_fastx_parser(path)
    if fmt is not expected_fmt:
        raise AssertionError
    for _ in parser:
        pass


def test_write_tmp_fasta_file():
    fpath, dpath = random.write_tmp_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    assert_fastx_file(fpath, const.FastxFormats.FASTA)
    zpath, _ = random.write_tmp_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN, dpath, gzipped=True
    )
    assert_fastx_file(zpath, const.FastxFormats.FASTA)
    shutil.rmtree(dpath)


def test_write_tmp_fastq_file():
    fpath, dpath = random.write_tmp_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    assert_fastx_file(fpath, const.FastxFormats.FASTQ)
    zpath, _ = random.write_tmp_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN, dpath, gzipped=True
    )
    assert_fastx_file(zpath, const.FastxFormats.FASTQ)
    shutil.rmtree(dpath)


def test_write_tmp_fastx_file():
    fpath, dpath = random.write_tmp_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    assert_fastx_file(fpath, const.FastxFormats.FASTA)
    zpath, _ = random.write_tmp_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN, dpath, gzipped=True
    )
    assert_fastx_file(zpath, const.FastxFormats.FASTA)
    fpath, _ = random.write_tmp_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN, dpath
    )
    assert_fastx_file(fpath, const.FastxFormats.FASTQ)
    zpath, _ = random.write_tmp_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN, dpath, gzipped=True
    )
    assert_fastx_file(zpath, const.FastxFormats.FASTQ)
    shutil.rmtree(dpath)
