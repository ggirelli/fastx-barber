"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import const, scripts
from fastx_barber import bedio, io, scriptio, seqio
from fastx_barber import flag, match, qual, trim

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    pass

__all__ = [
    "const",
    "scripts",
    "bedio",
    "io",
    "scriptio",
    "seqio",
    "flag",
    "match",
    "qual",
    "trim",
]
