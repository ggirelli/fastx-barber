"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.exception import enable_rich_assert
from fastx_barber.io import ChunkMerger
from fastx_barber.scripts import arguments as ap
from fastx_barber.seqio import SimpleFastxRecord, get_fastx_format
from fastx_barber.trim import get_fastx_trimmer
import joblib  # type: ignore
import logging
from rich.logging import RichHandler  # type: ignore
import sys
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "length",
        description="Trim a FASTX file by length.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file by length.",
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

    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=0,
        help="Number of bases to be trimmed. Default: 0",
    )
    parser.add_argument(
        "-s",
        "--side",
        type=int,
        default=5,
        choices=[3, 5],
        help="""Side to trim from. Either '5' for 5' (left/start),
        or '3' for 3' (right/end). Default: 5""",
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


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.threads = ap.check_threads(args.threads)
    args = scriptio.set_tempdir(args)

    if 0 == args.length:
        logging.info(
            "Trimming length (--length) equal to 0. Nothing to do. :person_shrugging:"
        )
        sys.exit()

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> Tuple[int, int]:
    fmt, _ = get_fastx_format(args.input)
    OHC = scriptio.get_chunk_handler(
        cid, fmt, args.output, args.compress_level, args.temp_dir
    )
    assert OHC is not None

    trimmer = get_fastx_trimmer(fmt)

    skipped_short_counter = 0
    trimmed_counter = 0
    for record in chunk:
        if len(record[1]) <= args.length:
            skipped_short_counter += 1
            continue
        record = trimmer.trim_len(record, args.length, args.side)
        OHC.write(record)
        trimmed_counter += 1

    OHC.close()

    return (trimmed_counter, skipped_short_counter)


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Trimming\t{args.length} nt from {args.side}'")
    logging.info(f"Threads\t\t{args.threads}")
    logging.info(f"Chunk size\t{args.chunk_size}")

    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    logging.info("[bold underline red]Running[/]")
    logging.info("Trimming...")
    output = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(
            chunk,
            cid,
            args,
        )
        for chunk, cid in IH
    )

    parsed_counter = 0
    trimmed_counter = 0
    for trimmed, skipped_short in output:
        trimmed_counter += trimmed
        parsed_counter += skipped_short
    parsed_counter += trimmed_counter
    logging.info(
        " ".join(
            (
                f"{trimmed_counter}/{parsed_counter}",
                f"({trimmed_counter/parsed_counter*100:.2f}%)",
                "records trimmed.",
            )
        )
    )

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir, None)
    merger.do(args.output, IH.last_chunk_id, "Writing trimmed records")

    logging.info("Done. :thumbs_up: :smiley:")
