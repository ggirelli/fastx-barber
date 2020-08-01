"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.const import __version__, logfmt, log_datefmt
from fbarber.extract import get_fastx_flag_extractor
from fbarber.match import FastxMatcher
from fbarber.seqio import get_fastx_parser, get_fastx_writer
from fbarber.trim import get_fastx_trimmer
import logging
import os
import regex  # type: ignore
import sys
from tqdm import tqdm  # type: ignore

logging.basicConfig(level=logging.INFO, format=logfmt, datefmt=log_datefmt)


def init_parser(subparsers: argparse._SubParsersAction
                ) -> argparse.ArgumentParser:
    """Initialize parser

    Arguments:
        subparsers {argparse._SubParsersAction}

    Returns:
        argparse.ArgumentParser -- parsed arguments
    """
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Extract flags from adapter and trim FASTX file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Extract flags from adapter and trim a FASTX file..")

    parser.add_argument("input", type=str, metavar="in.fastx[.gz]",
                        help="""Path to the fasta/q file to trim.""")
    parser.add_argument("output", type=str, metavar="out.fastx[.gz]",
                        help="""Path to fasta/q file where to write
                        trimmed records. Format will match the input.""")

    default_pattern = "^(?<UMI>.{8})(?<BC>GTCGTATC)(?<CS>GATC){s<2}"
    parser.add_argument(
        "--pattern", type=str, default=default_pattern,
        help=f"""Pattern to match to reads and extract flagged groups.
        Remember to use quotes. Default: '{default_pattern}'""")

    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}")

    advanced = parser.add_argument_group("advanced arguments")

    advanced.add_argument(
        "--unmatched-output", type=str, default=None,
        help="""Path to fasta/q file where to write records that do not match
        the pattern. Format will match the input.""")
    advanced.add_argument(
        "--flag-delim", type=str, default="~",
        help="""Delimiter for flags. Used twice for flag separation and once
        for key-value pairs. It should be a single character. Default: '~'.
        Example: header~~flag1key~flag1value~~flag2key~flag2value""")
    advanced.add_argument(
        "--selected-flags", type=str,
        help="""Comma-separate names of flags to be extracted.
        By default it extracts all flags.""")
    advanced.add_argument(
        "--comment-space", type=str, default=" ",
        help="""Delimiter for header comments. Defaults to a space.""")
    advanced.add_argument(
        "--compress-level", type=int, default=6,
        help="""GZip compression level. Default: 6.""")
    advanced.add_argument(
        "--log-file", type=str,
        help="""Path to file where to write the log.""")

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    """Parse arguments

    Arguments:
        args {argparse.Namespace} -- input arguments

    Returns:
        argparse.Namespace -- parsed arguments
    """
    args.regex = regex.compile(args.pattern)
    assert 1 == len(args.flag_delim)

    if args.log_file is not None:
        assert not os.path.isdir(args.log_file)
        log_dir = os.path.dirname(args.log_file)
        assert os.path.isdir(log_dir) or '' == log_dir
        fh = logging.FileHandler(args.log_file)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(logfmt))
        logging.getLogger('').addHandler(fh)
        logging.info(f"Writing log to: {args.log_file}")

    if args.selected_flags is not None:
        args.selected_flags = args.selected_flags.split(",")

    return args


def run(args: argparse.Namespace) -> None:
    """Run extract command

    Arguments:
        args {argparse.Namespace} -- input arguments
    """
    IH, fmt = get_fastx_parser(args.input)
    logging.info(f"Input: {args.input}")

    OH = get_fastx_writer(fmt)(args.output, args.compress_level)
    assert fmt == OH.format, (
        "format mismatch between input and requested output")
    logging.info(f"Output: {args.output}")

    if args.unmatched_output is not None:
        UH = get_fastx_writer(fmt)(args.unmatched_output, args.compress_level)
        assert fmt == UH.format, (
            "format mismatch between input and requested output")
        logging.info(f"Unmatched output: {args.unmatched_output}")
        foutput = {True: OH.write, False: UH.write}
    else:
        foutput = {True: OH.write, False: lambda x: None}

    logging.info(f"Pattern: {args.pattern}")

    matcher = FastxMatcher(args.regex)
    flag_extractor = get_fastx_flag_extractor(fmt)(args.selected_flags)
    flag_extractor.flag_delim = args.flag_delim
    flag_extractor.comment_space = args.comment_space
    trimmer = get_fastx_trimmer(fmt)

    logging.info("Trimming and extracting flags...")
    for record in tqdm(IH):
        match, matched = matcher.match(record)
        if matched:
            record = flag_extractor.update(record, match)
            record = trimmer.trim_re(record, match)
        foutput[matched](record)

    parsed_count = matcher.matched_count + matcher.unmatched_count

    logging.info("".join((
        f"Trimmed {matcher.matched_count}/{parsed_count} records.")))

    OH.close()
    if args.unmatched_output is not None:
        UH.close()
    logging.info("Done.")
