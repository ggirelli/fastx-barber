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
                        help="""Path to fasta/q file where to write
                        trimmed records. Format will match the input.""")

    parser.add_argument(
        "--pattern", type=str,
        help="Pattern to match to reads and extract flagged groups.",
        default="^(?<UMI>.{8})(?<BC>GTCGTATC)(?<CS>GATC){s<2}")

    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}")

    advanced = parser.add_argument_group("advanced arguments")

    advanced.add_argument(
        "--unmatched-output", type=str, default=None,
        help="""Path to fasta/q file where to write records that do not match
        the pattern. Format will match the input.""")

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

    if args.unmatched_output is not None:
        UH = SimpleFastxWriter(args.unmatched_output)
        assert fmt == UH.format, (
            "format mismatch between input and requested output")
        foutput = {True: OH.write_record, False: UH.write_record}
    else:
        foutput = {True: OH.write_record, False: lambda x: x}

    trimmer = FastxTrimmer(args.pattern, fmt)
    for record in tqdm(IH):
        record, is_trimmed = trimmer.trim(record)
        foutput[is_trimmed](record)

    OH.close()
    if args.unmatched_output is not None:
        UH.close()
