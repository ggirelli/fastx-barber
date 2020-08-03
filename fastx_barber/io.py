"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import os
from tqdm import tqdm  # type: ignore
from typing import Optional, Tuple


def is_gzipped(path: str) -> Tuple[str, str, bool]:
    """
    Returns:
        Tuple[str, str, bool] -- basename, extension, gzipped status
    """
    base, ext = os.path.splitext(path)
    return (base, ext, ".gz" == ext)


class ChunkMerger(object):
    """docstring for ChunkMerger"""

    _do_remove: bool = True

    def __init__(self, compress_level: int = 6):
        super(ChunkMerger, self).__init__()
        self.__compress_level = compress_level

    @property
    def do_remove(self) -> bool:
        return self._do_remove

    @do_remove.setter
    def do_remove(self, do_remove: bool) -> None:
        self._do_remove = do_remove

    def do(self, path: str, last_chunk_id: int, desc: Optional[str] = None) -> None:
        with open(path, "wb") as OH:
            for cid in tqdm(range(1, last_chunk_id + 1), desc=desc):
                chunk_path = f".tmp.batch{cid}.{path}"
                if not os.path.isfile(chunk_path):
                    continue
                with open(chunk_path, "rb") as CH:
                    OH.write(CH.read())
                if self._do_remove:
                    os.remove(chunk_path)
