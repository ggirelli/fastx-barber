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
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if record[1][5:] != trimmed_record[1]:
        raise AssertionError
    if record[2] != trimmed_record[2]:
        raise AssertionError

    trimmed_record = trimmer.trim_len(record, 5, 3)
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if record[1][:-5] != trimmed_record[1]:
        raise AssertionError
    if record[2] != trimmed_record[2]:
        raise AssertionError

    trimmed_record = trimmer.trim_len(record, 100, 3)
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "":
        raise AssertionError
    if record[2] != trimmed_record[2]:
        raise AssertionError


def test_FastaTrimmer_trim_re():
    trimmer = trim.FastaTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", None)

    matcher = match.FastxMatcher(re.compile("^.*CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "TGCAT":
        raise AssertionError
    if record[2] != trimmed_record[2]:
        raise AssertionError

    matcher = match.FastxMatcher(re.compile("^.*?CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "TCGATCGATGCAT":
        raise AssertionError
    if record[2] != trimmed_record[2]:
        raise AssertionError


def test_FastqTrimmer_trim_len():
    trimmer = trim.FastqTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", "A/A/A/A/A/A/A/A/A/A/A/")

    trimmed_record = trimmer.trim_len(record, 5, 5)
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if record[1][5:] != trimmed_record[1]:
        raise AssertionError
    if record[2][5:] != trimmed_record[2]:
        raise AssertionError

    trimmed_record = trimmer.trim_len(record, 5, 3)
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if record[1][:-5] != trimmed_record[1]:
        raise AssertionError
    if record[2][:-5] != trimmed_record[2]:
        raise AssertionError

    trimmed_record = trimmer.trim_len(record, 100, 3)
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "":
        raise AssertionError
    if trimmed_record[2] != "":
        raise AssertionError


def test_FastqTrimmer_trim_re():
    trimmer = trim.FastqTrimmer()
    record = ("test", "ATCGATCGATCGATCGATGCAT", "A/A/A/A/A/A/A/A/A/A/A/")

    matcher = match.FastxMatcher(re.compile("^.*CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "TGCAT":
        raise AssertionError
    if trimmed_record[2] != "/A/A/":
        raise AssertionError

    matcher = match.FastxMatcher(re.compile("^.*?CGATCGA"))
    trimmed_record = trimmer.trim_re(record, matcher.do(record)[0])
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "TCGATCGATGCAT":
        raise AssertionError
    if trimmed_record[2] != "/A/A/A/A/A/A/":
        raise AssertionError


def test_FastqTrimmer_trim_qual():
    trimmer = trim.FastqTrimmer()
    qio = qual.QualityIO()
    record = ("test", "ATCGATCGATCGATCGATGCAT", "////A/A/A/A/A/A/A/////")

    trimmed_record, trimmed_len = trimmer.trim_qual(record, 30, 5, qio)
    if trimmed_len != 4:
        raise AssertionError
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "ATCGATCGATCGATGCAT":
        raise AssertionError
    if trimmed_record[2] != "A/A/A/A/A/A/A/////":
        raise AssertionError

    trimmed_record, trimmed_len = trimmer.trim_qual(record, 30, 3, qio)
    if trimmed_len != 5:
        raise AssertionError
    if record[0] != trimmed_record[0]:
        raise AssertionError
    if trimmed_record[1] != "ATCGATCGATCGATCGA":
        raise AssertionError
    if trimmed_record[2] != "////A/A/A/A/A/A/A":
        raise AssertionError


def test_get_fastx_trimmer():
    if not isinstance(
        trim.get_fastx_trimmer(FastxFormats.FASTA), type(trim.FastaTrimmer)
    ):
        raise AssertionError
    if not isinstance(
        trim.get_fastx_trimmer(FastxFormats.FASTQ), type(trim.FastqTrimmer)
    ):
        raise AssertionError
    if not isinstance(trim.get_fastx_trimmer(FastxFormats.NONE), type(trim.ABCTrimmer)):
        raise AssertionError
