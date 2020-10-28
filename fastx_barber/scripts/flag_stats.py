"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.exception import enable_rich_assert
from fastx_barber.flag import FastxFlagReader, FlagStats
from fastx_barber.match import SimpleFastxRecord
from fastx_barber.scripts import arguments as ap
import joblib  # type: ignore
import logging
from rich.logging import RichHandler  # type: ignore
import sys
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "stats",
        description="Calculate FASTX flag stats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Calculate FASTX flag stats.",
    )

    parser.add_argument(
        "input",
        type=str,
        metavar="in.fastx[.gz]",
        help="Path to the fasta/q file to scan for matches.",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_flag_delim_option(advanced)
    advanced = ap.add_comment_space_option(advanced)
    advanced = ap.add_flagstats_option(advanced)

    advanced = ap.add_compress_level_option(advanced)
    advanced = ap.add_log_file_option(advanced)
    advanced = ap.add_chunk_size_option(advanced)
    advanced = ap.add_threads_option(advanced)
    advanced = ap.add_tempdir_option(advanced)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.threads = ap.check_threads(args.threads)
    args = scriptio.set_tempdir(args)

    if args.flagstats is None:
        logging.info(
            "No flag specified (--flagstats), nothing to do. :person_shrugging:"
        )
        sys.exit()

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> None:
    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    flag_reader = FastxFlagReader(args.flagstats)
    flag_reader.flag_delim = args.flag_delim
    flag_reader.comment_space = args.comment_space

    for record in chunk:
        flag_reader.read(record)

    return flag_reader.flagstats


def merge_flagstats(chunk_details: List[FlagStats]) -> FlagStats:
    flagstats: FlagStats = FlagStats()
    for stats in chunk_details:
        for flag_name, data in stats.items():
            for k, v in data.items():
                flagstats[flag_name][k] += v
    return flagstats


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Threads\t\t{args.threads}")
    logging.info(f"Chunk size\t{args.chunk_size}")
    logging.info("[bold underline red]Flag extraction[/]")
    logging.info(f"Flag delim\t'{args.flag_delim}'")
    logging.info(f"Comment delim\t'{args.comment_space}'")
    logging.info(f"Flag stats\t'{args.flagstats}'")

    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    logging.info("[bold underline red]Running[/]")
    logging.info("Matching...")
    chunk_details = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(
            chunk,
            cid,
            args,
        )
        for chunk, cid in IH
    )

    merge_flagstats(chunk_details).export(args.input)

    logging.info("Done. :thumbs_up: :smiley:")
