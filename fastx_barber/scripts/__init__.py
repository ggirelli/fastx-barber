"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.scripts import arguments
from fastx_barber.scripts import find_seq
from fastx_barber.scripts import flag, flag_extract
from fastx_barber.scripts import flag_filter, flag_regex, flag_split, flag_stats
from fastx_barber.scripts import match
from fastx_barber.scripts import trim, trim_len, trim_qual, trim_regex

__all__ = [
    "arguments",
    "find_seq",
    "flag",
    "flag_extract",
    "flag_filter",
    "flag_regex",
    "flag_split",
    "flag_stats",
    "match",
    "trim",
    "trim_len",
    "trim_qual",
    "trim_regex",
]
