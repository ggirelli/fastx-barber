"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.scripts import common as com
from fbarber.const import logfmt, log_datefmt
from fbarber.match import FastxMatcher
from fbarber.trim import get_fastx_trimmer
import logging
import regex  # type: ignore
from tqdm import tqdm  # type: ignore

logging.basicConfig(level=logging.INFO, format=logfmt, datefmt=log_datefmt)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Initialize parser

    Arguments:
        subparsers {argparse._SubParsersAction}

    Returns:
        argparse.ArgumentParser -- parsed arguments
    """
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Trim FASTX file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file.",
    )

    parser.add_argument(
        "input",
        type=str,
        metavar="in.fastx[.gz]",
        help="""Path to the fasta/q file to trim.""",
    )
    parser.add_argument(
        "output",
        type=str,
        metavar="out.fastx[.gz]",
        help="""Path to fasta/q file where to write
                        trimmed records. Format will match the input.""",
    )

    default_pattern = "^(?<UMI>.{8})(?<BC>GTCGTATC)(?<CS>GATC){s<2}"
    parser.add_argument(
        "--pattern",
        type=str,
        default=default_pattern,
        help=f"""Pattern to match to reads and trim.
        Remember to use quotes. Default: '{default_pattern}'""",
    )

    parser = com.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = com.add_unmatched_output_option(advanced)
    advanced = com.add_compress_level_option(advanced)
    advanced = com.add_log_file_option(advanced)

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

    if args.log_file is not None:
        com.add_log_file_handler(args)

    return args


def run(args: argparse.Namespace) -> None:
    """Run trim command

    Arguments:
        args {argparse.Namespace} -- input arguments
    """
    logging.info(f"Pattern: {args.pattern}")
    fmt, IH, OH, UH, foutput = com.get_io_handlers(args)

    matcher = FastxMatcher(args.regex)
    trimmer = get_fastx_trimmer(fmt)

    logging.info("Trimming...")
    for record in tqdm(IH):
        match, matched = matcher.match(record)
        if matched:
            record = trimmer.trim_re(record, match)
        foutput[matched](record)

    parsed_count = matcher.matched_count + matcher.unmatched_count

    logging.info("".join((f"Trimmed {matcher.matched_count}/{parsed_count} records.")))

    OH.close()
    if args.unmatched_output is not None and UH is not None:
        UH.close()
    logging.info("Done.")
