"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import match
import regex as re  # type: ignore


def test_AlphaNumericPattern():
    pass


def test_FastxMatcher():
    matcher = match.FastxMatcher(re.compile("GATC.{3}TTT"))
    if not matcher.do(("test", "GATCAAATTT", None))[1]:
        raise AssertionError
    if matcher.do(("test", "GATAAAATTT", None))[1]:
        raise AssertionError


def test_search_needle():
    record = ("test", "GATCACACATATATAGATCatcgatcagatcGATC", None)
    positions = list(match.search_needle(record, "GATC", 0))
    if positions[0] != (0, 1):
        raise AssertionError
    if positions[1] != (15, 2):
        raise AssertionError
    if positions[2] != (31, 3):
        raise AssertionError
    positions = list(match.search_needle(record, "gatc", 0))
    if positions[0] != (22, 1):
        raise AssertionError
    if positions[1] != (27, 2):
        raise AssertionError
