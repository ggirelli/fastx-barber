"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.match import SimpleFastxRecord
from fastx_barber.scripts import arguments as ap
import joblib  # type: ignore
import logging
from rich.logging import RichHandler
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Filter a FASTX file based on flag quality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Filter a FASTX file based on flag quality.",
    )

    parser.add_argument(
        "input",
        type=str,
        metavar="in.fastx[.gz]",
        help="""Path to the fasta/q file
                        to scan for matches.""",
    )
    parser.add_argument(
        "output",
        type=str,
        metavar="out.fastx[.gz]",
        help="""Path to fasta/q file where to write
                        matching records. Format will match the input.""",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_compress_level_option(advanced)
    advanced = ap.add_log_file_option(advanced)

    advanced = ap.add_chunk_size_option(advanced)
    advanced = ap.add_threads_option(advanced)
    advanced = ap.add_tempdir_option(advanced)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.threads = ap.check_threads(args.threads)
    args = scriptio.set_tempdir(args)

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> None:
    return


def run(args: argparse.Namespace) -> None:
    ap.log_args(args)

    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    logging.info("[bold underline red]Running[/]")
    logging.info("Matching...")
    joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(
            chunk,
            cid,
            args,
        )
        for chunk, cid in IH
    )

    logging.info("Done. :thumbs_up: :smiley:")
