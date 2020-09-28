"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import os
from rich.progress import track
import tempfile
from typing import Optional, Tuple


def is_gzipped(path: str) -> Tuple[str, str, bool]:
    """
    Returns:
        Tuple[str, str, bool] -- basename, extension, gzipped status
    """
    base, ext = os.path.splitext(path)
    return (base, ext, ".gz" == ext)


class ChunkMerger(object):
    _do_remove: bool = True
    _tempdir: Optional[tempfile.TemporaryDirectory]

    def __init__(
        self,
        tempdir: Optional[tempfile.TemporaryDirectory] = None,
    ):
        super(ChunkMerger, self).__init__()
        self._tempdir = tempdir

    @property
    def do_remove(self) -> bool:
        return self._do_remove

    @do_remove.setter
    def do_remove(self, do_remove: bool) -> None:
        self._do_remove = do_remove

    def do(self, path: str, last_chunk_id: int, desc: Optional[str] = None) -> None:
        with open(path, "wb") as OH:
            for cid in track(
                range(1, last_chunk_id + 1), description=desc, transient=False
            ):
                chunk_path = f".tmp.chunk{cid}.{path}"
                if self._tempdir is not None:
                    chunk_path = os.path.join(self._tempdir.name, chunk_path)
                if not os.path.isfile(chunk_path):
                    continue
                with open(chunk_path, "rb") as CH:
                    OH.write(CH.read())
                if self._do_remove:
                    os.remove(chunk_path)
