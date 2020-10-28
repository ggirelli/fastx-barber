"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import qual
from fastx_barber.const import DEFAULT_PHRED_OFFSET

DEFAULT_FILTER_QUAL_FLAGS = ["flag,30,.2", "test,15,.1"]


def test_QualityIO():
    qio = qual.QualityIO()
    assert 32 == qio.phred_to_qscore("A")[0]
    assert 14 == qio.phred_to_qscore("/")[0]
    assert 60 == qio.phred_to_qscore("]")[0]
    assert 36 == qio.phred_to_qscore("E")[0]
    assert [32, 14, 60, 36] == qio.phred_to_qscore("A/]E")
    qio = qual.QualityIO(64)
    assert 32 - 31 == qio.phred_to_qscore("A")[0]
    assert 60 - 31 == qio.phred_to_qscore("]")[0]
    assert 36 - 31 == qio.phred_to_qscore("E")[0]
    assert [1, 29, 5] == qio.phred_to_qscore("A]E")


def test_QualityFilter():
    qf = qual.QualityFilter(30, 0.2)
    assert qf.qual_pass_filter("AAAA")
    assert not qf.qual_pass_filter("/AAA")
    assert qf.qual_pass_filter("AE]]]/")
    assert 3 == qf.parsed
    assert 2 == qf.passed


def validate_filters(filters):
    assert "qflag" in filters
    assert isinstance(filters["qflag"], qual.QualityFilter)
    assert 30 == filters["qflag"].min_qscore
    assert 0.2 == filters["qflag"].max_perc
    assert "qtest" in filters
    assert isinstance(filters["qtest"], qual.QualityFilter)
    assert 15 == filters["qtest"].min_qscore
    assert 0.1 == filters["qtest"].max_perc


def test_QualityFilter_init_flag_filters():
    filters = qual.QualityFilter.init_flag_filters(
        DEFAULT_FILTER_QUAL_FLAGS, DEFAULT_PHRED_OFFSET
    )
    validate_filters(filters)


def test_dummy_apply_filter_flag():
    assert qual.dummy_apply_filter_flag({}, {})


def test_apply_filter_flag():
    filters = qual.QualityFilter.init_flag_filters(
        DEFAULT_FILTER_QUAL_FLAGS, DEFAULT_PHRED_OFFSET
    )
    assert qual.apply_filter_flag(
        {"qflag": ("AAAA", -1, -1), "qtest": ("AAAAAAAAA", -1, -1)}, filters
    )
    assert not qual.apply_filter_flag(
        {"qflag": ("/AAA", -1, -1), "qtest": ("AAAAAAAAA", -1, -1)}, filters
    )
    assert not qual.apply_filter_flag(
        {"qflag": ("AAAA", -1, -1), "qtest": ("/AAAAAAAA", -1, -1)}, filters
    )
    assert not qual.apply_filter_flag(
        {"qflag": ("/AAA", -1, -1), "qtest": ("/AAAAAAAA", -1, -1)}, filters
    )
    assert qual.apply_filter_flag(
        {"qflag": ("/EEAAAA", -1, -1), "qtest": ("/EEAAAAAAAA", -1, -1)}, filters
    )


def test_setup_qual_filters():
    qff, ff = qual.setup_qual_filters(None, DEFAULT_PHRED_OFFSET)
    assert 0 == len(qff)
    assert qual.dummy_apply_filter_flag == ff
    qff, ff = qual.setup_qual_filters(DEFAULT_FILTER_QUAL_FLAGS, DEFAULT_PHRED_OFFSET)
    assert 2 == len(qff)
    assert qual.apply_filter_flag == ff
    validate_filters(qff)
