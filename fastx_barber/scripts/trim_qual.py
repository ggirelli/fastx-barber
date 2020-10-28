"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.exception import enable_rich_assert
from fastx_barber.const import FastxFormats
from fastx_barber.io import ChunkMerger
from fastx_barber.qual import QualityIO
from fastx_barber.scripts import arguments as ap
from fastx_barber.seqio import (
    FastxChunkedParser,
    get_fastx_format,
    get_fastx_parser,
    SimpleFastqRecord,
)
from fastx_barber.trim import FastqTrimmer
import joblib  # type: ignore
import logging
import numpy as np  # type: ignore
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
        "quality",
        description="Trim a FASTQ file by quality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTQ file by quality.",
    )

    parser.add_argument(
        "input",
        type=str,
        metavar="in.fastq[.gz]",
        help="""Path to the fastq file to trim.""",
    )
    parser.add_argument(
        "output",
        type=str,
        metavar="out.fastq[.gz]",
        help="""Path to fastq file where to write
        trimmed records. Format will match the input.""",
    )

    parser.add_argument(
        "-q",
        "--qscore",
        type=int,
        default=0,
        help="QSCORE threshold. Any base with lower QSCORE is discarded. Default: 0",
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
    advanced = ap.add_phred_offset_option(advanced)
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

    if 0 == args.qscore:
        logging.info(
            "Trimming QSCORE threshold (-q) equal to 0. "
            + "Nothing to do. :person_shrugging:"
        )
        sys.exit()

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastqRecord],
    cid: int,
    args: argparse.Namespace,
) -> Tuple[int, int, List[int]]:
    fmt, _ = get_fastx_format(args.input)
    OHC = scriptio.get_chunk_handler(
        cid, fmt, args.output, args.compress_level, args.temp_dir
    )
    assert OHC is not None

    trimmer = FastqTrimmer()
    qio = QualityIO(args.phred_offset)

    trimmed_counter = 0
    untrimmed_counter = 0
    trimmed_length_list: List[int] = []
    for record in chunk:
        record, trimmed_length = trimmer.trim_qual(record, args.qscore, args.side, qio)
        trimmed_length_list.append(trimmed_length)
        if 0 < len(record[1]):
            OHC.write(record)
        trimmed_counter += trimmed_length != 0
        untrimmed_counter += trimmed_length == 0

    OHC.close()

    return (trimmed_counter, untrimmed_counter, trimmed_length_list)


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Trimming\tQSCORE < {args.qscore} from {args.side}'")
    logging.info(f"Threads\t\t{args.threads}")
    logging.info(f"Chunk size\t{args.chunk_size}")

    IH, fmt = get_fastx_parser(args.input)
    IH = FastxChunkedParser(IH, args.chunk_size)

    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)
    assert FastxFormats.FASTQ == fmt, "Trimming by quality requires a fastq file."

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

    trimmed_length_list: List[int] = []
    trimmed_counter = 0
    parsed_counter = 0
    for trimmed, untrimmed, trimmed_lengths in output:
        trimmed_counter += trimmed
        parsed_counter += untrimmed
        trimmed_length_list.extend(trimmed_lengths)
    parsed_counter += trimmed_counter
    logging.info(
        " ".join(
            (
                f"{trimmed_counter}/{parsed_counter}",
                f"({trimmed_counter/parsed_counter*100:.2f}%) records trimmed.",
            )
        )
    )
    logging.info("Trimmed length statistics: min\tmean\tmedian\tmax")
    logging.info(
        "\t".join(
            (
                f"                           {min(trimmed_length_list)}",
                f"{np.mean(trimmed_length_list):.3f}",
                f"{np.median(trimmed_length_list):.3f}",
                f"{max(trimmed_length_list)}",
            )
        )
    )

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir, None)
    merger.do(args.output, IH.last_chunk_id, "Writing trimmed records")

    logging.info("Done. :thumbs_up: :smiley:")
