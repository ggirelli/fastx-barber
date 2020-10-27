"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import match


def test_FastxMatcher():
    matcher = match.FastxMatcher("GATC.{3}TTT")
    assert matcher.do(("test", "GATCAAATTT", None))[1]
    assert not matcher.do(("test", "GATAAAATTT", None))[1]
