"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import match, qual, trim
from fastx_barber.const import FastxFormats
import regex as re  # type: ignore


def test_FastaTrimmer_trim_len():
    trimmer = trim.FastaTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", None)

    trimmed_record = trimmer.trim_len(record, 5, 5)
    assert record[0] == trimmed_record[0]
    assert record[1][5:] == trimmed_record[1]
    assert record[2] == trimmed_record[2]

    trimmed_record = trimmer.trim_len(record, 5, 3)
    assert record[0] == trimmed_record[0]
    assert record[1][:-5] == trimmed_record[1]
    assert record[2] == trimmed_record[2]

    trimmed_record = trimmer.trim_len(record, 100, 3)
    assert record[0] == trimmed_record[0]
    assert "" == trimmed_record[1]
    assert record[2] == trimmed_record[2]


def test_FastaTrimmer_trim_re():
    trimmer = trim.FastaTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", None)

    matcher = match.FastxMatcher(re.compile("^.*CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    assert record[0] == trimmed_record[0]
    assert "TGCAT" == trimmed_record[1]
    assert record[2] == trimmed_record[2]

    matcher = match.FastxMatcher(re.compile("^.*?CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    assert record[0] == trimmed_record[0]
    assert "TCGATCGATGCAT" == trimmed_record[1]
    assert record[2] == trimmed_record[2]


def test_FastqTrimmer_trim_len():
    trimmer = trim.FastqTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", "A/A/A/A/A/A/A/A/A/A/A/")

    trimmed_record = trimmer.trim_len(record, 5, 5)
    assert record[0] == trimmed_record[0]
    assert record[1][5:] == trimmed_record[1]
    assert record[2][5:] == trimmed_record[2]

    trimmed_record = trimmer.trim_len(record, 5, 3)
    assert record[0] == trimmed_record[0]
    assert record[1][:-5] == trimmed_record[1]
    assert record[2][:-5] == trimmed_record[2]

    trimmed_record = trimmer.trim_len(record, 100, 3)
    assert record[0] == trimmed_record[0]
    assert "" == trimmed_record[1]
    assert "" == trimmed_record[2]


def test_FastqTrimmer_trim_re():
    trimmer = trim.FastqTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", "A/A/A/A/A/A/A/A/A/A/A/")

    matcher = match.FastxMatcher(re.compile("^.*CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    assert record[0] == trimmed_record[0]
    assert "TGCAT" == trimmed_record[1]
    assert "/A/A/" == trimmed_record[2]

    matcher = match.FastxMatcher(re.compile("^.*?CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    assert record[0] == trimmed_record[0]
    assert "TCGATCGATGCAT" == trimmed_record[1]
    assert "/A/A/A/A/A/A/" == trimmed_record[2]


def test_FastqTrimmer_trim_qual():
    trimmer = trim.FastqTrimmer()
    qio = qual.QualityIO()
    record = ("test", "ATCGATCGATCGATCGATGCAT", "////A/A/A/A/A/A/A/////")

    trimmed_record, trimmed_len = trimmer.trim_qual(record, 30, 5, qio)
    assert 4 == trimmed_len
    assert record[0] == trimmed_record[0]
    assert "ATCGATCGATCGATGCAT" == trimmed_record[1]
    assert "A/A/A/A/A/A/A/////" == trimmed_record[2]

    trimmed_record, trimmed_len = trimmer.trim_qual(record, 30, 3, qio)
    assert 5 == trimmed_len
    assert record[0] == trimmed_record[0]
    assert "ATCGATCGATCGATCGA" == trimmed_record[1]
    assert "////A/A/A/A/A/A/A" == trimmed_record[2]


def test_get_fastx_trimmer():
    assert isinstance(
        trim.get_fastx_trimmer(FastxFormats.FASTA), type(trim.FastaTrimmer)
    )
    assert isinstance(
        trim.get_fastx_trimmer(FastxFormats.FASTQ), type(trim.FastqTrimmer)
    )
    assert isinstance(trim.get_fastx_trimmer(FastxFormats.NONE), type(trim.ABCTrimmer))
