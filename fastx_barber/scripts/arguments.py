"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import __version__, DEFAULT_PHRED_OFFSET
import joblib  # type: ignore
import logging
import sys
import tempfile


def log_args(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Pattern\t\t{args.pattern.pattern}")
    logging.info(f"Threads\t\t{args.threads}")
    logging.info(f"Chunk size\t{args.chunk_size}")


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
        help="""How many records per chunk. Default: 50000""",
    )
    return arg_group


def add_threads_option(arg_group: argparse._ArgumentGroup) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--threads",
        type=int,
        default=1,
        help="""Threads for parallelization. Default: 1""",
    )
    return arg_group


def add_tempdir_option(arg_group: argparse._ArgumentGroup) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--temp-dir",
        type=str,
        help="""Path to temporary folder.""",
        default=tempfile.gettempdir(),
    )
    return arg_group


def check_threads(threads: int) -> int:
    if threads > joblib.cpu_count():
        return joblib.cpu_count()
    elif threads <= 0:
        return 1
    return threads


def add_phred_offset_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--phred-offset",
        type=str,
        default=DEFAULT_PHRED_OFFSET,
        help="""Phred offset for qscore calculation.""",
    )
    return arg_group


def add_flag_delim_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--flag-delim",
        type=str,
        default="~",
        help="""Delimiter for flags. Used twice for flag separation and once
        for key-value pairs. It should be a single character. Default: '~'.
        Example: header~~flag1key~flag1value~~flag2key~flag2value""",
    )
    return arg_group


def add_filter_qual_flags_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--filter-qual-flags",
        type=str,
        nargs="+",
        help="""Space-separated 'flag_name,min_qscore,max_perc' strings, where
        bases with qscore < min_qscore are considered low quality, and max_perc
        is the largest allowed fraction of low quality bases. I.e., you can specify
        multiple flag filters by separating them with a space.""",
    )
    return arg_group


def add_filter_qual_output_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--filter-qual-output",
        type=str,
        help="""Path to fasta/q file where to write records that do not pass the
        flag filters. Format must match the input.""",
    )
    return arg_group


def add_comment_space_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--comment-space",
        type=str,
        default=" ",
        help="""Delimiter for header comments. Defaults to a space.""",
    )
    return arg_group


def add_split_by_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--split-by",
        type=str,
        help="""Flag to be used to split records in separate output files,
        based on flag value.""",
    )
    return arg_group


def add_flagstats_option(
    arg_group: argparse._ArgumentGroup,
) -> argparse._ArgumentGroup:
    arg_group.add_argument(
        "--flagstats",
        type=str,
        nargs="+",
        help="""Space-separate names of flags to calculate statistics for. By default
        this is skipped. Statistics are calculated before any quality filter, on records
        matching the provided pattern.""",
    )
    return arg_group
