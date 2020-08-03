"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.scripts import common as com
from fastx_barber.const import logfmt, log_datefmt
from fastx_barber.io import ChunkMerger
from fastx_barber.match import FastxMatcher, SimpleFastxRecord
from fastx_barber.seqio import get_fastx_format
import joblib  # type: ignore
import logging
import regex  # type: ignore
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format=logfmt, datefmt=log_datefmt)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Scan FASTX file for matches.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Scan a FASTX file for matches.",
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

    default_pattern = "^(?<UMI>.{8})(?<BC>CATCACGC){s<2}(?<CS>GATC){s<2}"
    parser.add_argument(
        "--pattern",
        type=str,
        default=default_pattern,
        help=f"""Pattern to match to reads.
        Remember to use quotes. Default: '{default_pattern}'""",
    )

    parser = com.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = com.add_unmatched_output_option(advanced)
    advanced = com.add_compress_level_option(advanced)
    advanced = com.add_log_file_option(advanced)

    advanced = com.add_chunk_size_option(advanced)
    advanced = com.add_threads_option(advanced)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    args.regex = regex.compile(args.pattern)
    args.threads = com.check_threads(args.threads)

    if args.log_file is not None:
        com.add_log_file_handler(args.log_file)

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord], cid: int, args: argparse.Namespace,
) -> Tuple[int, int]:
    fmt, _ = get_fastx_format(args.input)
    OHC = com.get_chunk_handler(cid, fmt, args.output, args.compress_level)
    assert OHC is not None
    UHC = com.get_chunk_handler(cid, fmt, args.unmatched_output, args.compress_level)
    foutput = com.get_output_fun(OHC, UHC)

    matcher = FastxMatcher(args.regex)

    for record in chunk:
        match, matched = matcher.match(record)
        foutput[matched](record)

    OHC.close()
    if UHC is not None:
        UHC.close()

    return (matcher.matched_count, len(chunk))


def run(args: argparse.Namespace) -> None:
    logging.info(f"Threads: {args.threads}")
    logging.info(f"Chunk size: {args.chunk_size}")
    logging.info(f"Pattern: {args.pattern}")

    fmt, IH = com.get_input_handler(args.input, args.compress_level, args.chunk_size)

    logging.info("Matching...")
    output = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(chunk, cid, args,) for chunk, cid in IH
    )

    parsed_counter = 0
    matched_counter = 0
    for matched, parsed in output:
        matched_counter += matched
        parsed_counter += parsed
    logging.info(f"{matched_counter}/{parsed_counter} records matched the pattern.")

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.compress_level)
    merger.do(args.output, IH.last_chunk_id, "Matched")
    if args.unmatched_output is not None:
        merger.do(args.unmatched_output, IH.last_chunk_id, "Unmatched")

    logging.info("Done.")
