"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.const import __version__
from fbarber.match import FastxMatcher
from fbarber.seqio import get_fastx_parser, get_fastx_writer
from fbarber.trim import get_fastx_trimmer
import logging
import os
import regex  # type: ignore
import sys
from tqdm import tqdm  # type: ignore
from typing import Any, Dict


def init_parser(subparsers: argparse._SubParsersAction
                ) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Trim FASTX file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file..")

    parser.add_argument("input", type=str, metavar="in.fastx[.gz]",
                        help="""Path to the fasta/q file to trim.""")
    parser.add_argument("output", type=str, metavar="out.fastx[.gz]",
                        help="""Path to fasta/q file where to write
                        trimmed records. Format will match the input.""")

    default_pattern = "^(?<UMI>.{8})(?<BC>GTCGTATC)(?<CS>GATC){s<2}"
    parser.add_argument(
        "--pattern", type=str, default=default_pattern,
        help=f"""Pattern to match to reads and trim.
        Remember to use quotes. Default: '{default_pattern}'""")

    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}")

    advanced = parser.add_argument_group("advanced arguments")

    advanced.add_argument(
        "--unmatched-output", type=str, default=None,
        help="""Path to fasta/q file where to write records that do not match
        the pattern. Format will match the input.""")
    advanced.add_argument(
        "--compress-level", type=int, default=6,
        help="""GZip compression level. Default: 6.""")
    advanced.add_argument(
        "--log-file", type=str,
        help="""Path to file where to write the log.""")

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.regex = regex.compile(args.pattern)

    assert not os.path.isfile(args.log_file)
    assert os.path.isdir(os.path.dirname(args.log_file))
    log_settings: Dict[str, Any] = {
        "level": 20,
        "format": "".join((
            "%(asctime)s [P%(process)s:%(module)s:%(funcName)s] ",
            "%(levelname)s: %(message)s")),
        "datefmt": "%m/%d/%Y %I:%M:%S"}
    if args.log_file is not None:
        log_settings['filename'] = open(args.log_file, "w+")
    logging.basicConfig(**log_settings)

    return args


def run(args: argparse.Namespace) -> None:
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
    trimmer = get_fastx_trimmer(fmt)

    logging.info("Trimming...")
    for record in tqdm(IH):
        match, matched = matcher.match(record)
        if matched:
            record = trimmer.trim_re(record, match)
        foutput[matched](record)

    parsed_count = matcher.matched_count + matcher.unmatched_count

    logging.info("".join((
        f"Trimmed {matcher.matched_count}/{parsed_count} records.")))

    OH.close()
    if args.unmatched_output is not None:
        UH.close()
    logging.info("Done.")
