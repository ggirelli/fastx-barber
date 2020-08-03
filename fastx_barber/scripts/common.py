"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import __version__, logfmt, FastxFormats
from fastx_barber.qual import dummy_apply_filter_flag, apply_filter_flag
from fastx_barber.qual import QualityFilter
from fastx_barber.seqio import (
    get_fastx_parser,
    get_fastx_writer,
    FastxChunkedParser,
    SimpleFastxParser,
    SimpleFastxWriter,
)
import joblib  # type: ignore
import logging
import os
import sys
import tempfile
from typing import Callable, Dict, Optional, Tuple


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
    fh = logging.FileHandler(path, mode="w+")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(logfmt))
    logging.getLogger(logger_name).addHandler(fh)
    logging.info(f"Writing log to: {path}")


def get_input_handler(
    path: str, compress_level: int, chunk_size: int
) -> Tuple[
    FastxFormats, SimpleFastxParser,
]:
    IH, fmt = get_fastx_parser(path)
    logging.info(f"Input: {path}")
    IH = FastxChunkedParser(IH, chunk_size)
    return (fmt, IH)


def get_chunk_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Optional[SimpleFastxWriter]:
    if path is None:
        return None
    chunk_path = f".tmp.chunk{cid}.{path}"
    if tempdir is not None:
        chunk_path = os.path.join(tempdir.name, os.path.basename(chunk_path))
    assert not os.path.isdir(path)
    return get_fastx_writer(fmt)(chunk_path, compress_level)


def get_output_fun(
    OH: Optional[SimpleFastxWriter], UH: Optional[SimpleFastxWriter]
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
        return {True: OH.write, False: lambda x: None}


def setup_qual_filters(
    filter_qual_flags: str, phred_offset: int, verbose: bool = False
) -> Tuple[Dict[str, QualityFilter], Callable]:
    if verbose:
        logging.info(f"PHRED offset: {phred_offset}")
    quality_flag_filters: Dict[str, QualityFilter] = {}
    filter_fun = dummy_apply_filter_flag
    if filter_qual_flags is not None:
        quality_flag_filters = QualityFilter.init_flag_filters(
            filter_qual_flags.split(" "), phred_offset
        )
        if verbose:
            for name, f in quality_flag_filters.items():
                logging.info(
                    f"{name}-filter: min_score={f.min_qscore} & max_perc={f.max_perc}"
                )
        filter_fun = apply_filter_flag
    return (quality_flag_filters, filter_fun)


def get_qual_filter_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Tuple[Optional[SimpleFastxWriter], Callable]:
    FH = get_chunk_handler(cid, fmt, path, compress_level, tempdir)
    if FH is not None:
        assert fmt == FH.format, "format mismatch between input and requested output"
        return (FH, FH.write)
    else:
        return (FH, lambda x: None)


def add_version_option(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}"
    )
    return parser


def add_unmatched_output_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--unmatched-output",
        type=str,
        help="""Path to fasta/q file where to write records that do not match
        the pattern. Format must match the input.""",
    )
    return arg_group


def add_compress_level_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--compress-level",
        type=int,
        default=6,
        help="""GZip compression level. Default: 6.""",
    )
    return arg_group


def add_log_file_option(arg_group: argparse._ArgumentGroup) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--log-file", type=str, help="""Path to file where to write the log."""
    )
    return arg_group


def add_chunk_size_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--chunk-size",
        type=int,
        default=50000,
        help=f"""How many records per chunk. Default: 50000""",
    )
    return arg_group


def add_threads_option(arg_group: argparse._ArgumentGroup) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--threads",
        type=int,
        default=1,
        help=f"""Threads for parallelization. Default: 1""",
    )
    return arg_group


def check_threads(threads: int) -> int:
    if threads > joblib.cpu_count():
        return joblib.cpu_count()
    elif threads <= 0:
        return 1
    return threads


def add_tempdir_option(arg_group: argparse._ArgumentGroup) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--temp-dir",
        type=str,
        help="""Path to temporary folder.""",
        default=tempfile.gettempdir(),
    )
    return arg_group
