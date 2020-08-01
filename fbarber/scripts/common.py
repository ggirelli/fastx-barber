"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.const import __version__, logfmt, FastxFormats
from fbarber.seqio import get_fastx_parser, get_fastx_writer
from fbarber.seqio import FastXParser, SimpleFastxWriter
import logging
import os
import sys
from typing import Callable, Dict, Optional, Tuple


def add_log_file_handler(args: argparse.Namespace) -> None:
    assert not os.path.isdir(args.log_file)
    log_dir = os.path.dirname(args.log_file)
    assert os.path.isdir(log_dir) or "" == log_dir
    fh = logging.FileHandler(args.log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(logfmt))
    logging.getLogger("").addHandler(fh)
    logging.info(f"Writing log to: {args.log_file}")


def get_io_handlers(
    args: argparse.Namespace,
) -> Tuple[
    FastxFormats,
    FastXParser,
    SimpleFastxWriter,
    Optional[SimpleFastxWriter],
    Dict[bool, Callable],
]:
    IH, fmt = get_fastx_parser(args.input)
    logging.info(f"Input: {args.input}")

    OH = get_fastx_writer(fmt)(args.output, args.compress_level)
    assert fmt == OH.format, "format mismatch between input and requested output"
    logging.info(f"Output: {args.output}")

    UH: Optional[SimpleFastxWriter]
    if args.unmatched_output is not None:
        UH = get_fastx_writer(fmt)(args.unmatched_output, args.compress_level)
        assert fmt == UH.format, "format mismatch between input and requested output"
        logging.info(f"Unmatched output: {args.unmatched_output}")
        foutput = {True: OH.write, False: UH.write}
    else:
        UH = None
        foutput = {True: OH.write, False: lambda x: None}

    return (fmt, IH, OH, UH, foutput)


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
