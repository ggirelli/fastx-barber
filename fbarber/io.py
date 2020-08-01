"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import os
from typing import Tuple


def is_gzipped(path: str) -> Tuple[str, str, bool]:
    """Check if a file is gzipped

    The check is only based on the file extension

    Arguments:
        path {str} -- path to file to be checked
    """
    base, ext = os.path.splitext(path)
    return (base, ext, ".gz" == ext)
