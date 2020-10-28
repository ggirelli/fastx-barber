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
from fastx_barber.qual import setup_qual_filters
from fastx_barber.scriptio import get_handles
from fastx_barber.scripts import arguments as ap
from fastx_barber.seqio import SimpleFastxWriter
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
        "filter",
        description="Filter a FASTX file based on flag quality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Filter a FASTX file based on flag quality.",
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
    advanced = ap.add_filter_qual_flags_option(advanced)
    advanced = ap.add_filter_qual_output_option(advanced)
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

    if args.filter_qual_flags is None:
        logging.info("No quality filter specified, nothing to do. :person_shrugging:")
        sys.exit()

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    args.unmatched_output = None

    return args


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> Tuple[int, int]:
    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)
    OHC, _, FHC, filter_output_fun = get_handles(fmt, cid, args)
    foutput = scriptio.get_output_fun(OHC, None)

    quality_flag_filters, filter_fun = setup_qual_filters(
        args.filter_qual_flags, args.phred_offset
    )

    flag_reader = FastxFlagReader()
    flag_reader.flag_delim = args.flag_delim
    flag_reader.comment_space = args.comment_space

    unfiltered_counter = 0
    filtered_counter = 0
    for record in chunk:
        flags = flag_reader.read(record)
        pass_filters = filter_fun(flags, quality_flag_filters)
        if pass_filters:
            unfiltered_counter += 1
            foutput[True](record, flags)
        else:
            filtered_counter += 1
            filter_output_fun(record, flags)

    SimpleFastxWriter.close_handle(OHC)
    SimpleFastxWriter.close_handle(FHC)

    return (filtered_counter, unfiltered_counter)


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
    quality_flag_filters, filter_fun = setup_qual_filters(
        args.filter_qual_flags, args.phred_offset, verbose=True
    )

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
    unfiltered_counter = 0
    for filtered, unfiltered in chunk_details:
        parsed_counter += filtered
        unfiltered_counter += unfiltered
    parsed_counter += unfiltered_counter
    logging.info(
        " ".join(
            (
                f"{unfiltered_counter}/{parsed_counter}",
                f"({unfiltered_counter/parsed_counter*100:.2f}%)",
                "records passed the filter(s).",
            )
        )
    )

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir)
    merger.do(args.output, IH.last_chunk_id, "Writing matched records")
    if args.filter_qual_output is not None:
        merger.do(args.filter_qual_output, IH.last_chunk_id, "Writing filtered records")

    logging.info("Done. :thumbs_up: :smiley:")
