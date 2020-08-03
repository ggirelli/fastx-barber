"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import __version__, logfmt, FastxFormats
from fastx_barber.seqio import get_fastx_parser, get_fastx_writer
from fastx_barber.seqio import FastXParser, SimpleFastxWriter
import logging
import os
import sys
from typing import Callable, Dict, IO, Optional, Tuple


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
    fh = logging.FileHandler(path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(logfmt))
    logging.getLogger(logger_name).addHandler(fh)
    logging.info(f"Writing log to: {path}")


def get_io_handlers(
    ipath: str, opath: str, compress_level: int
) -> Tuple[
    FastxFormats, FastXParser, SimpleFastxWriter,
]:
    """Prepare IO handlers.

    Arguments:
        ipath {str} -- path to input file
        opath {str} -- path to output file
        compress_level {int} -- compression level
    """
    IH, fmt = get_fastx_parser(ipath)
    logging.info(f"Input: {ipath}")

    OH = get_fastx_writer(fmt)(opath, compress_level)
    assert fmt == OH.format, "format mismatch between input and requested output"
    logging.info(f"Output: {opath}")

    return (fmt, IH, OH)


def get_unmatched_handler(
    fmt: FastxFormats, upath: Optional[str], compress_level: int
) -> Optional[SimpleFastxWriter]:
    """Prepare output buffer handler for unmatched records.

    Arguments:
        upath {Optional[str]} -- path to output file for unmatched records
        compress_level {int} -- compression level
    """
    UH: Optional[SimpleFastxWriter]
    if upath is not None:
        UH = get_fastx_writer(fmt)(upath, compress_level)
        assert fmt == UH.format, "format mismatch between input and requested output"
        logging.info(f"Unmatched output: {upath}")
    else:
        UH = None
    return UH


def get_output_fun(
    OH: SimpleFastxWriter, UH: Optional[SimpleFastxWriter]
) -> Dict[bool, Callable]:
    """Prepare IO handlers.

    Arguments:
        OH {IO} -- output buffer handler
        UH {Optional[SimpleFastxWriter]} -- unmatched output buffer handler
    """
    if UH is not None:
        return {True: OH.write, False: UH.write}
    else:
        return {True: OH.write, False: lambda x: None}


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
        default=None,
        help="""Path to fasta/q file where to write records that do not match
        the pattern. Format will match the input.""",
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
