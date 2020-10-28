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
    assert matcher.do(("test", "GATCAAATTT", None))[1]
    assert not matcher.do(("test", "GATAAAATTT", None))[1]


def test_search_needle():
    record = ("test", "GATCACACATATATAGATCatcgatcagatcGATC", None)
    positions = [x for x in match.search_needle(record, "GATC", 0)]
    assert positions[0] == (0, 1)
    assert positions[1] == (15, 2)
    assert positions[2] == (31, 3)
    positions = [x for x in match.search_needle(record, "gatc", 0)]
    assert positions[0] == (22, 1)
    assert positions[1] == (27, 2)
