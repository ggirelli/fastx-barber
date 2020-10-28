"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import io, bedio, scriptio, seqio
from fastx_barber.const import FastxFormats
from fastx_barber.exception import enable_rich_assert
from fastx_barber.match import search_needle
from fastx_barber.scripts import arguments as ap
import logging
import os
from rich.logging import RichHandler  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Scan a FASTX file for a sequence.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Scan a FASTX file a sequence and generate a BED file with its locations.",
    )

    parser.add_argument(
        "input",
        type=str,
        metavar="in.fastx[.gz]",
        help="""Path to the fasta/q file to scan for matches.""",
    )
    parser.add_argument(
        "needle",
        type=str,
        help="""Sequence to scan for.""",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced.add_argument(
        "--output",
        type=str,
        metavar="out.bed[.gz]",
        help="Path to fasta/q file where to write trimmed records. "
        + "Format will match the input. Defaults to input file with BED extension.",
    )
    advanced.add_argument(
        "--prefix",
        type=str,
        metavar="prefix",
        help="""Name prefix. Default: 'loc_'""",
        default="loc_",
    )
    advanced.add_argument(
        "--case-insensitive",
        action="store_const",
        dest="case_insensitive",
        const=True,
        default=False,
        help="Perform case-insensitive scan.",
    )
    advanced.add_argument(
        "--global-name",
        action="store_const",
        dest="global_name",
        const=True,
        default=False,
        help="Global location name. Requires sorted FASTA.",
    )
    advanced = ap.add_compress_level_option(advanced)
    advanced = ap.add_log_file_option(advanced)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    assert os.path.isfile(args.input), f"file not found: '{args.input}'"

    fmt, _ = seqio.get_fastx_format(args.input)
    assert fmt in [
        FastxFormats.FASTA,
        FastxFormats.FASTQ,
    ], f"input must be a FASTX file. ({fmt})"

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    if args.output is None:
        base, ext, gzipped = io.is_gzipped(args.input)
        args.output = f"{base}.bed"
        if gzipped:
            args.output += ".gz"

    if args.case_insensitive:
        args.needle = args.needle.upper()

    return args


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Needle\t\t{args.needle}")
    logging.info(f"Output\t\t{args.output}")
    logging.info(f"Prefix\t\t{args.prefix}")
    logging.info(f"Global\t\t{args.global_name}")

    parser, fmt = seqio.get_fastx_parser(args.input)

    writer = bedio.BedWriter(args.output, 4)

    location_id = 0
    for record in parser:
        if args.case_insensitive:
            record[1] = record[1].upper()
        for pos, location_id in search_needle(record, args.needle, location_id):
            writer.do(
                (
                    record[0],
                    pos,
                    pos + len(args.needle) + 1,
                    f"{args.prefix}{location_id}",
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                )
            )
        if not args.global_name:
            location_id = 0

    logging.info("Done. :thumbs_up: :smiley:")
