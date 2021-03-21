"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from enum import Enum
from typing import DefaultDict, Optional, Tuple

__version__ = "0.1.3"


BedRecord = Tuple[
    str,
    int,
    int,
    Optional[str],
    Optional[float],
    Optional[str],
    Optional[int],
    Optional[int],
    Optional[str],
    Optional[int],
    Optional[int],
    Optional[int],
]
BedExtension = ".bed"


class FastxFormats(Enum):
    """Fastx formats

    Extends:
        Enum

    Variables:
        FASTA {str}
        FASTQ {str}
        NONE {str} -- Not fastx
    """

    FASTA = "fasta"
    FASTQ = "fastq"
    NONE = "None"

    @classmethod
    def has_value(self, value):
        return value in self._value2member_map_


class FastxExtensions(Enum):
    """Fastx extensions

    Extends:
        Enum

    Variables:
        FASTA {tuple}
        FASTQ {tuple}
    """

    FASTA = (".fa", ".fasta")
    FASTQ = (".fq", ".fastq")

    @classmethod
    def has_value(self, value):
        return any(value in v for v in self._value2member_map_)


QFLAG_START = "q"
DEFAULT_PHRED_OFFSET = 33

PATTERN_EXAMPLE = "^(?<UMI>.{8})(?<BC>.{8})(?<CS>GATC){s<2}"

"""Flag data, contains matched str, start, and end position"""
FlagData = Tuple[str, int, int]
FlagStatsType = DefaultDict[str, DefaultDict[str, int]]

# Unit tests related stuff
UT_FLAG_NAME = "fake"
UT_RECORD_SEQ_LEN = 200
UT_N_RECORDS = 100
UT_CHUNK_SIZE = 8
UT_FLAG_PATTERN = f"^(?<{UT_FLAG_NAME}>.{{8}})"
