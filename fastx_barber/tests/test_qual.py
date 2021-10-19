"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import qual
from fastx_barber.const import DEFAULT_PHRED_OFFSET

DEFAULT_FILTER_QUAL_FLAGS = ["flag,30,.2", "test,15,.1"]


def test_QualityIO():
    qio = qual.QualityIO()
    if 32 != qio.phred_to_qscore("A")[0]:
        raise AssertionError
    if 14 != qio.phred_to_qscore("/")[0]:
        raise AssertionError
    if 60 != qio.phred_to_qscore("]")[0]:
        raise AssertionError
    if 36 != qio.phred_to_qscore("E")[0]:
        raise AssertionError
    if [32, 14, 60, 36] != qio.phred_to_qscore("A/]E"):
        raise AssertionError
    qio = qual.QualityIO(64)
    if 32 - 31 != qio.phred_to_qscore("A")[0]:
        raise AssertionError
    if 60 - 31 != qio.phred_to_qscore("]")[0]:
        raise AssertionError
    if 36 - 31 != qio.phred_to_qscore("E")[0]:
        raise AssertionError
    if [1, 29, 5] != qio.phred_to_qscore("A]E"):
        raise AssertionError


def test_QualityFilter():
    qf = qual.QualityFilter(30, 0.2)
    if not qf.qual_pass_filter("AAAA"):
        raise AssertionError
    if qf.qual_pass_filter("/AAA"):
        raise AssertionError
    if not qf.qual_pass_filter("AE]]]/"):
        raise AssertionError
    if 3 != qf.parsed:
        raise AssertionError
    if 2 != qf.passed:
        raise AssertionError


def validate_filters(filters):
    if "qflag" not in filters:
        raise AssertionError
    if not isinstance(filters["qflag"], qual.QualityFilter):
        raise AssertionError
    if 30 != filters["qflag"].min_qscore:
        raise AssertionError
    if 0.2 != filters["qflag"].max_perc:
        raise AssertionError
    if "qtest" not in filters:
        raise AssertionError
    if not isinstance(filters["qtest"], qual.QualityFilter):
        raise AssertionError
    if 15 != filters["qtest"].min_qscore:
        raise AssertionError
    if 0.1 != filters["qtest"].max_perc:
        raise AssertionError


def test_QualityFilter_init_flag_filters():
    filters = qual.QualityFilter.init_flag_filters(
        DEFAULT_FILTER_QUAL_FLAGS, DEFAULT_PHRED_OFFSET
    )
    validate_filters(filters)


def test_dummy_apply_filter_flag():
    if not qual.dummy_apply_filter_flag({}, {}):
        raise AssertionError


def test_apply_filter_flag():
    filters = qual.QualityFilter.init_flag_filters(
        DEFAULT_FILTER_QUAL_FLAGS, DEFAULT_PHRED_OFFSET
    )
    if not qual.apply_filter_flag(
        {"qflag": ("AAAA", -1, -1), "qtest": ("AAAAAAAAA", -1, -1)}, filters
    ):
        raise AssertionError
    if qual.apply_filter_flag(
        {"qflag": ("/AAA", -1, -1), "qtest": ("AAAAAAAAA", -1, -1)}, filters
    ):
        raise AssertionError
    if qual.apply_filter_flag(
        {"qflag": ("AAAA", -1, -1), "qtest": ("/AAAAAAAA", -1, -1)}, filters
    ):
        raise AssertionError
    if qual.apply_filter_flag(
        {"qflag": ("/AAA", -1, -1), "qtest": ("/AAAAAAAA", -1, -1)}, filters
    ):
        raise AssertionError
    if not qual.apply_filter_flag(
        {"qflag": ("/EEAAAA", -1, -1), "qtest": ("/EEAAAAAAAA", -1, -1)}, filters
    ):
        raise AssertionError


def test_setup_qual_filters():
    qff, ff = qual.setup_qual_filters(None, DEFAULT_PHRED_OFFSET)
    if 0 != len(qff):
        raise AssertionError
    if qual.dummy_apply_filter_flag != ff:
        raise AssertionError
    qff, ff = qual.setup_qual_filters(DEFAULT_FILTER_QUAL_FLAGS, DEFAULT_PHRED_OFFSET)
    if 2 != len(qff):
        raise AssertionError
    if qual.apply_filter_flag != ff:
        raise AssertionError
    validate_filters(qff)
