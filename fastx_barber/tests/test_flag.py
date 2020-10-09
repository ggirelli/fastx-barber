"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import const, flag


def test_FlagStats():
    pass


def test_FastaFlagExtractor():
    pass


def test_FastqFlagExtractor():
    pass


def test_get_fastx_flag_extractor():
    assert (
        flag.get_fastx_flag_extractor(const.FastxFormats.FASTA)
        is flag.FastaFlagExtractor
    )
    assert (
        flag.get_fastx_flag_extractor(const.FastxFormats.FASTQ)
        is flag.FastqFlagExtractor
    )
    assert (
        flag.get_fastx_flag_extractor(const.FastxFormats.NONE) is flag.ABCFlagExtractor
    )


def test_FastxFlagReader():
    pass


def test_FlagRegexes():
    pass
