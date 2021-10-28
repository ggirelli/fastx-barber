"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.exception import enable_rich_assert
from fastx_barber.flag import FastxFlagReader
from fastx_barber.io import ChunkMerger
from fastx_barber.match import SimpleFastxRecord
from fastx_barber.scriptio import get_split_chunk_handler
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
        "split",
        description="Split FASTX by flag value.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Split FASTX by flag value.",
    )

    parser.add_argument(
        "input",
        type=str,
        metavar="in.fastx[.gz]",
        help="Path to the fasta/q file to scan for matches.",
    )
    parser.add_argument(
        "output",
        type=str,
        metavar="out.fastx[.gz]",
        help="Path to fasta/q file where to write matching records. "
        + "Format will match the input.",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_flag_delim_option(advanced)
    advanced = ap.add_comment_space_option(advanced)
    advanced = ap.add_split_by_option(advanced)

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

    if args.split_by is None:
        logging.info(
            "No flag specified (--split-by), nothing to do. :person_shrugging:"
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
    OHC = get_split_chunk_handler(
        cid, fmt, args.output, args.compress_level, args.split_by, args.temp_dir
    )
    if OHC is None:
        raise AssertionError

    flag_reader = FastxFlagReader()
    flag_reader.flag_delim = args.flag_delim
    flag_reader.comment_space = args.comment_space

    for record in chunk:
        flags = flag_reader.read(record)
        if flags is not None:
            OHC.write(record, flags)
        else:
            logging.warning("encountered record without flags.")


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Threads\t\t{args.threads}")
    logging.info(f"Chunk size\t{args.chunk_size}")
    logging.info("[bold underline red]Flag extraction[/]")
    logging.info(f"Flag delim\t'{args.flag_delim}'")
    logging.info(f"Comment delim\t'{args.comment_space}'")
    logging.info(f"Split by\t'{args.split_by}'")

    _, IH = scriptio.get_input_handler(args.input, args.chunk_size)

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

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir, args.split_by)
    merger.do(args.output, IH.last_chunk_id, "Writing matched records")

    logging.info("Done. :thumbs_up: :smiley:")
