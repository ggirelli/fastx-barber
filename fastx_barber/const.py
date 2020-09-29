"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from enum import Enum
from typing import DefaultDict, Tuple

__version__ = "0.1.0b"


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

DEFAULT_PATTERN = "^(?<UMI>.{8})(?<BC>.{8})(?<CS>GATC){s<2}"

"""Flag data, contains matched str, start, and end position"""
FlagData = Tuple[str, int, int]
FlagStats = DefaultDict[str, DefaultDict[str, int]]
