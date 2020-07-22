"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.const import __version__
from fbarber.seqio import get_fastx_parser
from fbarber.seqio import SimpleFastxWriter
from fbarber.trim import FastxTrimmer
import regex
import sys
from tqdm import tqdm


def init_parser(subparsers: argparse._SubParsersAction
                ) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1], description="""
Trim FASTX file.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file..")

    parser.add_argument("input", type=str, metavar="in.fastx[.gz]",
                        help="""Path to the fasta/q file to trim.""")
    parser.add_argument("output", type=str, metavar="out.fastx[.gz]",
                        help="""Path to the fasta/q file to trim.
                        Format will match the input.""")

    parser.add_argument(
        "--pattern", type=str,
        help="Pattern to match to reads and extract flagged groups.",
        default="^(?<UMI>.{8})(?<BC>GTCGTATC){s<2}(?<CS>GATC){s<2}")

    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}")

    # advanced = parser.add_argument_group("advanced arguments")

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.pattern = regex.compile(args.pattern)
    return args


def run(args: argparse.Namespace) -> None:
    IH, fmt = get_fastx_parser(args.input)
    OH = SimpleFastxWriter(args.output)
    assert fmt == OH.format, (
        "format mismatch between input and requested output")
    trimmer = FastxTrimmer(args.pattern, fmt)
    for record in tqdm(IH):
        trimmed, is_trimmed = trimmer.trim(record)
        if is_trimmed:
            OH.write_record(trimmed)
    OH.close()
