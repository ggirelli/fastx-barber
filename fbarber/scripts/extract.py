"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.scripts import common as com
from fbarber.const import logfmt, log_datefmt
from fbarber.extract import FastqFlagExtractor, get_fastx_flag_extractor
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
        description="Extract flags from adapter and trim FASTX file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Extract flags from adapter and trim a FASTX file.",
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
        help=f"""Pattern to match to reads and extract flagged groups.
        Remember to use quotes. Default: '{default_pattern}'""",
    )

    parser = com.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = com.add_unmatched_output_option(advanced)
    advanced.add_argument(
        "--flag-delim",
        type=str,
        default="~",
        help="""Delimiter for flags. Used twice for flag separation and once
        for key-value pairs. It should be a single character. Default: '~'.
        Example: header~~flag1key~flag1value~~flag2key~flag2value""",
    )
    advanced.add_argument(
        "--selected-flags",
        type=str,
        help="""Comma-separate names of flags to be extracted.
        By default it extracts all flags.""",
    )
    advanced.add_argument(
        "--no-qual-flags",
        action="store_const",
        dest="qual_flags",
        const=False,
        default=True,
        help="""Do not extract quality flags
        (when running on a fastq file).""",
    )
    advanced.add_argument(
        "--comment-space",
        type=str,
        default=" ",
        help="""Delimiter for header comments. Defaults to a space.""",
    )
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
    assert 1 == len(args.flag_delim)

    if args.log_file is not None:
        com.add_log_file_handler(args)

    if args.selected_flags is not None:
        args.selected_flags = args.selected_flags.split(",")

    return args


def run(args: argparse.Namespace) -> None:
    """Run extract command

    Arguments:
        args {argparse.Namespace} -- input arguments
    """
    logging.info(f"Pattern: {args.pattern}")
    fmt, IH, OH, UH, foutput = com.get_io_handlers(args)

    matcher = FastxMatcher(args.regex)
    trimmer = get_fastx_trimmer(fmt)
    flag_extractor = get_fastx_flag_extractor(fmt)(args.selected_flags)
    flag_extractor.flag_delim = args.flag_delim
    flag_extractor.comment_space = args.comment_space
    if isinstance(flag_extractor, FastqFlagExtractor):
        flag_extractor.extract_qual_flags = args.qual_flags

    logging.info("Trimming and extracting flags...")
    for record in tqdm(IH):
        match, matched = matcher.match(record)
        if matched:
            record = flag_extractor.update(record, match)
            record = trimmer.trim_re(record, match)
        foutput[matched](record)

    parsed_count = matcher.matched_count + matcher.unmatched_count

    logging.info("".join((f"Trimmed {matcher.matched_count}/{parsed_count} records.")))

    OH.close()
    if args.unmatched_output is not None and UH is not None:
        UH.close()
    logging.info("Done.")
