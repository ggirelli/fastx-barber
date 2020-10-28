"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import glob
import os
from rich.progress import track  # type: ignore
import tempfile
from typing import Optional, Tuple


DTEMP_PREFIX = "fbarber_tmp."


def check_tmp_dir(path: Optional[str] = None) -> str:
    if path is not None:
        assert os.path.isdir(path)
    else:
        path = tempfile.mkdtemp(prefix=DTEMP_PREFIX)
    return path


def splitext(path: str) -> Tuple[str, str]:
    base, ext = os.path.splitext(path)
    ext_final = ext
    while ".gz" == ext:
        base, ext = os.path.splitext(base)
        ext_final = ext + ext_final
    return (base, ext_final)


def is_gzipped(path: str) -> Tuple[str, str, bool]:
    """
    Returns:
        Tuple[str, str, bool] -- basename, extension, gzipped status
    """
    base, ext = splitext(path)
    gzipped = ext.endswith(".gz")
    if gzipped:
        ext = ".".join(ext.split(".")[:-1])
    return (base, ext, gzipped)


class ChunkMerger(object):
    _do_remove: bool = True
    _tempdir: Optional[tempfile.TemporaryDirectory]
    _split_by: Optional[str] = None

    def __init__(
        self,
        tempdir: Optional[tempfile.TemporaryDirectory] = None,
        split_by: Optional[str] = None,
    ):
        super(ChunkMerger, self).__init__()
        self._tempdir = tempdir
        self._split_by = split_by

    @property
    def do_remove(self) -> bool:
        return self._do_remove

    @do_remove.setter
    def do_remove(self, do_remove: bool) -> None:
        self._do_remove = do_remove

    def __merge_simple(
        self, path: str, last_chunk_id: int, desc: Optional[str] = None
    ) -> None:
        with open(path, "wb") as OH:
            for cid in track(
                range(1, last_chunk_id + 1), description=desc, transient=False
            ):
                chunk_path = f".tmp.chunk{cid}.{os.path.basename(path)}"
                if self._tempdir is not None:
                    chunk_path = os.path.join(self._tempdir.name, chunk_path)
                if not os.path.isfile(chunk_path):
                    continue
                with open(chunk_path, "rb") as CH:
                    OH.write(CH.read())
                if self._do_remove:
                    os.remove(chunk_path)

    def __merge_split(
        self, path: str, last_chunk_id: int, desc: Optional[str] = None
    ) -> None:
        output_dir = os.path.dirname(path)
        output_base = os.path.basename(path)
        for cid in track(
            range(1, last_chunk_id + 1), description=desc, transient=False
        ):
            chunk_path = f"{self._split_by}_split.*.tmp.chunk{cid}.{output_base}"
            if self._tempdir is not None:
                chunk_path = os.path.join(self._tempdir.name, chunk_path)
            flist = glob.glob(chunk_path)
            for fname in flist:
                split_value = (
                    os.path.basename(fname).split("_split.")[1].split(".tmp.chunk")[0]
                )
                with open(
                    os.path.join(
                        output_dir,
                        f"{self._split_by}_split.{split_value}.{output_base}",
                    ),
                    "ab",
                ) as OH:
                    with open(fname, "rb") as CH:
                        OH.write(CH.read())
                    if self._do_remove:
                        os.remove(fname)

    def do(self, path: str, last_chunk_id: int, desc: Optional[str] = None) -> None:
        if self._split_by is None:
            self.__merge_simple(path, last_chunk_id, desc)
        else:
            self.__merge_split(path, last_chunk_id, desc)
