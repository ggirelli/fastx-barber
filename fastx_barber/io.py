"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import os
from typing import Tuple


def is_gzipped(path: str) -> Tuple[str, str, bool]:
    """
    Returns:
        Tuple[str, str, bool] -- basename, extension, gzipped status
    """
    base, ext = os.path.splitext(path)
    return (base, ext, ".gz" == ext)
