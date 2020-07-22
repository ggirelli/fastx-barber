"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fbarber.const import __version__
from fbarber.seqio import get_fastx_parser
from fbarber.seqio import SimpleFastxWriter
import logging
import sys

logging.basicConfig(
    level=20, format="".join((
        "%(asctime)s [P%(process)s:%(module)s:%(funcName)s] ",
        "%(levelname)s: %(message)s")), datefmt="%m/%d/%Y %I:%M:%S")


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
    parser.add_argument("length", type=int,
                        help="Length to trim.")

    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}")

    # advanced = parser.add_argument_group("advanced arguments")

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    assert 1 >= args.length
    return args


def run(args: argparse.Namespace) -> None:
    IH, fmt = get_fastx_parser(args.input)
    logging.info(f"Input: {args.input}")

    OH = SimpleFastxWriter(args.output, args.compress_level)
    assert fmt == OH.format, (
        "format mismatch between input and requested output")
    logging.info(f"Output: {args.output}")

    raise NotImplementedError

    OH.close()
    logging.info("Done.")
