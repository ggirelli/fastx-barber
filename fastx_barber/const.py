"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from enum import Enum

__version__ = "0.0.1"

logfmt = "".join(
    ("%(asctime)s ", "[P%(process)s:%(module)s] ", "%(levelname)s: %(message)s",)
)
log_datefmt = "%m/%d/%Y %I:%M:%S"


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
