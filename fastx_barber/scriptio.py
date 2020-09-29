"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import FastxFormats
from fastx_barber.seqio import (
    get_fastx_parser,
    get_fastx_writer,
    get_split_fastx_writer,
    FastxChunkedParser,
    SimpleFastxParser,
    SimpleFastxWriter,
    SimpleSplitFastxWriter,
)
import logging
import os
from rich.console import Console
from rich.logging import RichHandler
import tempfile
from typing import Callable, Dict, Optional, Tuple, Union


def set_tempdir(args: argparse.Namespace) -> argparse.Namespace:
    assert os.path.isdir(args.temp_dir), f"temporary folder not found: {args.temp_dir}"
    args.temp_dir = tempfile.TemporaryDirectory(
        prefix="fastx-barber.", dir=args.temp_dir
    )
    return args


def add_log_file_handler(path: str, logger_name: str = "") -> None:
    """Adds log file handler to logger.

    By defaults, adds the handler to the root logger.

    Arguments:
        path {str} -- path to output log file

    Keyword Arguments:
        logger_name {str} -- logger name (default: {""})
    """
    assert not os.path.isdir(path)
    log_dir = os.path.dirname(path)
    assert os.path.isdir(log_dir) or "" == log_dir
    fh = RichHandler(console=Console(file=open(path, mode="w+")), markup=True)
    fh.setLevel(logging.INFO)
    logging.getLogger(logger_name).addHandler(fh)
    logging.info(f"[green]Log to[/]\t\t{path}")


def get_input_handler(
    path: str, chunk_size: int
) -> Tuple[FastxFormats, SimpleFastxParser]:
    IH, fmt = get_fastx_parser(path)
    IH = FastxChunkedParser(IH, chunk_size)
    return (fmt, IH)


def get_chunk_tmp_path(
    cid: int,
    path: str,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> str:
    chunk_path = f".tmp.chunk{cid}.{path}"
    if tempdir is not None:
        chunk_path = os.path.join(tempdir.name, os.path.basename(chunk_path))
    return chunk_path


def get_chunk_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Optional[SimpleFastxWriter]:
    if path is None:
        return None
    chunk_path = get_chunk_tmp_path(cid, path, tempdir)
    assert not os.path.isdir(path)
    return get_fastx_writer(fmt)(chunk_path, compress_level)


def get_split_chunk_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    split_by: str,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Optional[SimpleSplitFastxWriter]:
    if path is None:
        return None
    chunk_path = get_chunk_tmp_path(cid, path, tempdir)
    assert not os.path.isdir(path)
    return get_split_fastx_writer(fmt)(chunk_path, split_by, compress_level)


def get_output_fun(
    OH: Union[SimpleFastxWriter, SimpleSplitFastxWriter, None],
    UH: Optional[SimpleFastxWriter],
) -> Dict[bool, Callable]:
    """Prepare IO handlers.

    Arguments:
        OH {Optional[SimpleFastxWriter]} -- output buffer handler
        UH {Optional[SimpleFastxWriter]} -- unmatched output buffer handler
    """
    assert OH is not None
    if UH is not None:
        return {True: OH.write, False: UH.write}
    else:
        return {True: OH.write, False: lambda *x: None}
