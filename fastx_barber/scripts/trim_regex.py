"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.exception import enable_rich_assert
from fastx_barber.const import PATTERN_EXAMPLE
from fastx_barber.io import ChunkMerger
from fastx_barber.match import FastxMatcher
from fastx_barber.scripts import arguments as ap
from fastx_barber.seqio import SimpleFastxRecord, get_fastx_format
from fastx_barber.trim import get_fastx_trimmer
import joblib  # type: ignore
import logging
import regex  # type: ignore
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
        "regex",
        description="Trim a FASTX file using a regular expression.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file using a regular expression.",
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
        help="Path to fasta/q file where to write trimmed records. "
        + "Format will match the input.",
    )

    parser.add_argument(
        "--pattern",
        type=str,
        help="Pattern to match to reads and trim. "
        + f"Remember to use quotes. Example: '{PATTERN_EXAMPLE}'",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_unmatched_output_option(advanced)
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

    if args.pattern is None:
        logging.info(
            "No pattern specified (--pattern), nothing to do. :person_shrugging:"
        )
        sys.exit()
    args.pattern = regex.compile(args.pattern)

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
):
    fmt, _ = get_fastx_format(args.input)
    OHC = scriptio.get_chunk_handler(
        cid, fmt, args.output, args.compress_level, args.temp_dir
    )
    assert OHC is not None
    UHC = scriptio.get_chunk_handler(
        cid, fmt, args.unmatched_output, args.compress_level, args.temp_dir
    )
    foutput = scriptio.get_output_fun(OHC, UHC)

    matcher = FastxMatcher(args.pattern)
    trimmer = get_fastx_trimmer(fmt)

    for record in chunk:
        match, matched = matcher.do(record)
        if matched:
            record = trimmer.trim_re(record, match)
        foutput[matched](record)

    OHC.close()
    if UHC is not None:
        UHC.close()

    return (matcher.matched_count, len(chunk))


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    ap.log_args(args)

    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    logging.info("[bold underline red]Running[/]")
    logging.info("Trimming...")
    chunk_details = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(
            chunk,
            cid,
            args,
        )
        for chunk, cid in IH
    )

    parsed_counter = 0
    matched_counter = 0
    for matched, parsed in chunk_details:
        matched_counter += matched
        parsed_counter += parsed
    logging.info(
        " ".join(
            (
                f"{matched_counter}/{parsed_counter}",
                f"({matched_counter/parsed_counter*100:.2f}%)",
                "records matched the pattern.",
            )
        )
    )

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir, None)
    merger.do(args.output, IH.last_chunk_id, "Writing matched records")
    if args.unmatched_output is not None:
        merger.do(args.unmatched_output, IH.last_chunk_id, "Writing unmatched records")

    logging.info("Done. :thumbs_up: :smiley:")
