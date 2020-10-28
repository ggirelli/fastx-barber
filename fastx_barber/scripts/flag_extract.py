"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scriptio
from fastx_barber.const import PATTERN_EXAMPLE, FlagData
from fastx_barber.exception import enable_rich_assert
from fastx_barber.flag import (
    FastqFlagExtractor,
    FlagStats,
    get_fastx_flag_extractor,
)
from fastx_barber.io import ChunkMerger
from fastx_barber.match import AlphaNumericPattern, FastxMatcher
from fastx_barber.qual import setup_qual_filters
from fastx_barber.scriptio import get_handles, get_split_handles
from fastx_barber.scripts import arguments as ap
from fastx_barber.seqio import (
    get_fastx_format,
    SimpleFastxRecord,
    SimpleFastxWriter,
    SimpleSplitFastxWriter,
)
from fastx_barber.trim import get_fastx_trimmer
import joblib  # type: ignore
import logging
import regex as re  # type: ignore
from rich.logging import RichHandler  # type: ignore
import sys
from typing import Dict, List, Tuple, Union

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "extract",
        description="Extract flags and trim the records of a FASTX file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Extract flags and trim the records of a FASTX file.",
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
        help="Pattern to match to reads and extract flagged groups. "
        + f"Remember to use quotes. Example: '{PATTERN_EXAMPLE}'",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_unmatched_output_option(advanced)
    advanced = ap.add_flag_delim_option(advanced)
    advanced.add_argument(
        "--selected-flags",
        type=str,
        nargs="+",
        help="Space-separated names of flags to be extracted. "
        + "By default it extracts all flags.",
    )
    advanced = ap.add_flagstats_option(advanced)
    advanced = ap.add_split_by_option(advanced)
    advanced = ap.add_filter_qual_flags_option(advanced)
    advanced = ap.add_filter_qual_output_option(advanced)
    advanced = ap.add_phred_offset_option(advanced)
    advanced.add_argument(
        "--no-qual-flags",
        action="store_const",
        dest="qual_flags",
        const=False,
        default=True,
        help="Do not extract quality flags (when running on a fastq file).",
    )
    advanced.add_argument(
        "--simple-pattern",
        action="store_const",
        dest="simple_pattern",
        const=True,
        default=False,
        help="Parse pattern as 'simple' (alphanumeric) pattern.",
    )
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
    assert 1 == len(args.flag_delim)
    args.threads = ap.check_threads(args.threads)
    args = scriptio.set_tempdir(args)

    if args.pattern is None:
        logging.info(
            "No pattern specified (--pattern), nothing to do. :person_shrugging:"
        )
        sys.exit()

    args.pattern = (
        AlphaNumericPattern(args.pattern)
        if args.simple_pattern
        else re.compile(args.pattern)
    )

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    ap.log_args(args)
    logging.info("[bold underline red]Flag extraction[/]")
    if args.selected_flags is not None:
        logging.info(f"Selected flags\t{args.selected_flags}")
    logging.info(f"Flag stats\t{args.flagstats}")
    logging.info(f"Flag delim\t'{args.flag_delim}'")
    logging.info(f"Comment delim\t'{args.comment_space}'")
    logging.info(f"Quality flags\t{args.qual_flags}")
    if args.split_by is not None:
        logging.info(f"Split by\t'{args.split_by}'")

    return args


ChunkDetails = Tuple[int, int, int, FlagStats]


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> ChunkDetails:
    fmt, _ = get_fastx_format(args.input)
    OHC: Union[SimpleFastxWriter, SimpleSplitFastxWriter, None]
    FHC: Union[SimpleFastxWriter, SimpleSplitFastxWriter, None]
    OHC, UHC, FHC, filter_output_fun = (
        get_handles(fmt, cid, args)
        if args.split_by is None
        else get_split_handles(fmt, cid, args)
    )
    foutput = scriptio.get_output_fun(OHC, UHC)

    matcher = FastxMatcher(args.pattern)
    trimmer = get_fastx_trimmer(fmt)
    quality_flag_filters, filter_fun = setup_qual_filters(
        args.filter_qual_flags, args.phred_offset
    )

    flag_extractor = get_fastx_flag_extractor(fmt)(args.selected_flags, args.flagstats)
    flag_extractor.flag_delim = args.flag_delim
    flag_extractor.comment_space = args.comment_space
    if isinstance(flag_extractor, FastqFlagExtractor):
        flag_extractor.extract_qual_flags = args.qual_flags

    filtered_counter = 0
    for record in chunk:
        flags: Dict[str, FlagData] = {}
        match, matched = matcher.do(record)
        if matched:
            flags = flag_extractor.extract_all(record, match)
            flag_extractor.update_stats(flags)
            flags_selected = flag_extractor.apply_selection(flags)
            record = flag_extractor.update(record, flags_selected)
            record = trimmer.trim_re(record, match)
            pass_filters = filter_fun(flags, quality_flag_filters)
            if not pass_filters:
                filtered_counter += 1
                filter_output_fun(record, flags)
                continue
        foutput[matched](record, flags)

    SimpleFastxWriter.close_handle(OHC)
    SimpleFastxWriter.close_handle(UHC)
    SimpleFastxWriter.close_handle(FHC)

    return (
        filtered_counter,
        matcher.matched_count,
        len(chunk),
        flag_extractor.flagstats,
    )


def merge_chunk_details(chunk_details: List[ChunkDetails]) -> ChunkDetails:
    parsed_counter = 0
    matched_counter = 0
    filtered_counter = 0
    flagstats: FlagStats = FlagStats()
    for filtered, matched, parsed, stats in chunk_details:
        filtered_counter += filtered
        matched_counter += matched
        parsed_counter += parsed
        for flag_name, data in stats.items():
            for k, v in data.items():
                flagstats[flag_name][k] += v
    return (parsed_counter, matched_counter, filtered_counter, flagstats)


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    fmt, IH = scriptio.get_input_handler(args.input, args.chunk_size)

    quality_flag_filters, filter_fun = setup_qual_filters(
        args.filter_qual_flags, args.phred_offset, verbose=True
    )

    logging.info("[bold underline red]Running[/]")
    logging.info("Trimming and extracting flags...")
    chunk_details = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(chunk, cid, args) for chunk, cid in IH
    )
    logging.info("Merging subprocesses details...")
    n_parsed, n_matched, n_filtered, flagstats = merge_chunk_details(chunk_details)

    logging.info(
        f"{n_matched}/{n_parsed} ({n_matched/n_parsed*100:.2f}%) "
        + "records matched the pattern.",
    )
    if args.filter_qual_flags is not None and 0 != n_matched:
        logging.info(
            " ".join(
                (
                    f"{(n_matched-n_filtered)}/{n_matched}",
                    f"({(n_matched-n_filtered)/n_matched*100:.2f}%)",
                    "records passed the quality filters.",
                )
            )
        )

    if args.flagstats is not None:
        flagstats.export(args.output)

    logging.info("Merging batch output...")
    if args.unmatched_output is not None:
        merger = ChunkMerger(args.temp_dir, None)
        merger.do(args.unmatched_output, IH.last_chunk_id, "Writing unmatched records")
    merger = ChunkMerger(args.temp_dir, args.split_by)
    merger.do(args.output, IH.last_chunk_id, "Writing matched records")
    if args.filter_qual_output is not None:
        merger.do(args.filter_qual_output, IH.last_chunk_id, "Writing filtered records")

    logging.info("Done. :thumbs_up: :smiley:")
