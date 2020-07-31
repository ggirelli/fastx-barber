'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from enum import Enum

__version__ = "0.0.1"


class FastxFormats(Enum):
    FASTA = "fasta"
    FASTQ = "fastq"
    NONE = "None"

    @classmethod
    def has_value(self, value):
        return value in self._value2member_map_


class FastxExtensions(Enum):
    FASTA = (".fa", ".fasta")
    FASTQ = (".fq", ".fastq")

    @classmethod
    def has_value(self, value):
        return any(value in v for v in self._value2member_map_)
