"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.scripts import arguments as ap
import logging
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

    parser.add_argument(
        "--output",
        type=str,
        metavar="out.bed[.gz]",
        help="Path to fasta/q file where to write trimmed records. "
        + "Format will match the input. Defaults to input file with BED extension.",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_compress_level_option(advanced)
    advanced = ap.add_log_file_option(advanced)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.threads = ap.check_threads(args.threads)

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Needle\t\t{args.nedle}")
    logging.info(f"Threads\t\t{args.threads}")

    logging.info("Done. :thumbs_up: :smiley:")
