"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.exception import enable_rich_assert
from fastx_barber.flag import FastxFlagReader, FlagRegexes
from fastx_barber.io import ChunkMerger
from fastx_barber.match import SimpleFastxRecord
from fastx_barber.scriptio import get_chunk_handler
from fastx_barber.scripts import arguments as ap
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
        "regex",
        description="Filter FASTX flags by regex.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Filter FASTX flags by regex.",
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

    parser.add_argument(
        "--pattern",
        type=str,
        nargs="+",
        help="Space-separated 'flag_name,pattern' strings. "
        + "Please wrap each string in quotes.",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_unmatched_output_option(advanced)
    advanced = ap.add_flag_delim_option(advanced)
    advanced = ap.add_comment_space_option(advanced)

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

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> Tuple[int, int]:
    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    OHC = get_chunk_handler(cid, fmt, args.output, args.compress_level, args.temp_dir)
    assert OHC is not None
    UHC = get_chunk_handler(
        cid, fmt, args.unmatched_output, args.compress_level, args.temp_dir
    )
    foutput = scriptio.get_output_fun(OHC, UHC)
    flag_regex = FlagRegexes(args.pattern)

    flag_reader = FastxFlagReader()
    flag_reader.flag_delim = args.flag_delim
    flag_reader.comment_space = args.comment_space

    matched_counter = 0
    unmatched_counter = 0
    for record in chunk:
        flags = flag_reader.read(record)
        if flags is not None:
            matched = flag_regex.match(flags)
            foutput[matched](record)
            matched_counter += matched
            unmatched_counter += not matched
        else:
            logging.warning("encountered record without flags.")

    return (matched_counter, unmatched_counter)


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("[bold underline red]General[/]")
    logging.info(f"Input\t\t{args.input}")
    logging.info(f"Threads\t\t{args.threads}")
    logging.info(f"Chunk size\t{args.chunk_size}")
    logging.info("[bold underline red]Flag extraction[/]")
    logging.info(f"Flag delim\t'{args.flag_delim}'")
    logging.info(f"Comment delim\t'{args.comment_space}'")

    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)
    FlagRegexes(args.pattern).log()

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

    parsed_counter = 0
    matched_counter = 0
    for matched, unmatched in chunk_details:
        matched_counter += matched
        parsed_counter += unmatched
    parsed_counter += matched_counter
    logging.info(
        " ".join(
            (
                f"{matched_counter}/{parsed_counter}",
                f"({matched_counter/parsed_counter*100:.2f}%)",
                "records matched the pattern(s).",
            )
        )
    )

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir, None)
    if args.unmatched_output is not None:
        merger.do(args.unmatched_output, IH.last_chunk_id, "Writing unmatched records")
    merger.do(args.output, IH.last_chunk_id, "Writing matched records")

    logging.info("Done. :thumbs_up: :smiley:")
