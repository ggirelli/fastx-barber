"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.const import __version__
from fbarber.seqio import get_fastx_handler
from fbarber.trim import FastxTrimmer
import sys


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

    parser.add_argument(
        "--pattern", type=str,
        help="""""", default="test")

    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}")

    # advanced = parser.add_argument_group("advanced arguments")

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    return args


def run(args: argparse.Namespace) -> None:
    IH, fmt = get_fastx_handler(args.input)
    trimmer = FastxTrimmer(args.pattern, fmt)
    for record in IH:
        trimmer.trim(record)
