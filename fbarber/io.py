'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

import os
from typing import Tuple


def is_gzipped(path: str) -> Tuple[str, str, bool]:
    base, ext = os.path.splitext(path)
    return (base, ext, ".gz" == ext)
