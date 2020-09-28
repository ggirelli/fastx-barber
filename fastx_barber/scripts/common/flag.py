"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import FastxFormats
from fastx_barber.flag import (
    get_fastx_flag_extractor,
    ABCFlagExtractor,
    FastqFlagExtractor,
)


def get_flag_extractor(fmt: FastxFormats, args: argparse.Namespace) -> ABCFlagExtractor:
    flag_extractor = get_fastx_flag_extractor(fmt)(args.selected_flags)
    flag_extractor.flag_delim = args.flag_delim
    flag_extractor.comment_space = args.comment_space
    if isinstance(flag_extractor, FastqFlagExtractor):
        flag_extractor.extract_qual_flags = args.qual_flags
    return flag_extractor
