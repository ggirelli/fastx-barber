"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import DEFAULT_PHRED_OFFSET
from fastx_barber.io import ChunkMerger
from fastx_barber.match import FastxMatcher
from fastx_barber.scripts.common import argparse as ap
from fastx_barber.scripts.common import io as scriptio
from fastx_barber.scripts.common import flag, qual
from fastx_barber.seqio import get_fastx_format, SimpleFastxRecord, SimpleFastxWriter
from fastx_barber.trim import get_fastx_trimmer
import joblib  # type: ignore
import logging
import regex  # type: ignore
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
        description="Extract flags from adapter and trim FASTX file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Extract flags from adapter and trim a FASTX file.",
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

    default_pattern = "^(?<UMI>.{8})(?<BC>CATCACGC){s<2}(?<CS>GATC){s<2}"
    parser.add_argument(
        "--pattern",
        type=str,
        default=default_pattern,
        help=f"""Pattern to match to reads and extract flagged groups.
        Remember to use quotes. Default: '{default_pattern}'""",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced = ap.add_unmatched_output_option(advanced)
    advanced.add_argument(
        "--flag-delim",
        type=str,
        default="~",
        help="""Delimiter for flags. Used twice for flag separation and once
        for key-value pairs. It should be a single character. Default: '~'.
        Example: header~~flag1key~flag1value~~flag2key~flag2value""",
    )
    advanced.add_argument(
        "--selected-flags",
        type=str,
        help="""Comma-separate names of flags to be extracted.
        By default it extracts all flags.""",
    )
    advanced.add_argument(
        "--filter-qual-flags",
        type=str,
        help="""Comma-separated 'flag_name,min_qscore,max_perc' strings, where
        bases with qscore < min_qscore are considered low quality, and max_perc
        is the largest allowed fraction of low quality bases. You can specify
        multiple flag filters by separating them with a space.""",
    )
    advanced.add_argument(
        "--filter-qual-output",
        type=str,
        help="""Path to fasta/q file where to write records that do not pass the
        flag filters. Format must match the input.""",
    )
    advanced.add_argument(
        "--phred-offset",
        type=str,
        default=DEFAULT_PHRED_OFFSET,
        help="""Phred offset for qscore calculation.""",
    )
    advanced.add_argument(
        "--no-qual-flags",
        action="store_const",
        dest="qual_flags",
        const=False,
        default=True,
        help="""Do not extract quality flags
        (when running on a fastq file).""",
    )
    advanced.add_argument(
        "--comment-space",
        type=str,
        default=" ",
        help="""Delimiter for header comments. Defaults to a space.""",
    )
    advanced = ap.add_compress_level_option(advanced)
    advanced = ap.add_log_file_option(advanced)

    advanced = ap.add_chunk_size_option(advanced)
    advanced = ap.add_threads_option(advanced)
    advanced = ap.add_tempdir_option(advanced)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    assert 1 == len(args.flag_delim)
    args.threads = ap.check_threads(args.threads)
    args = scriptio.set_tempdir(args)

    if args.log_file is not None:
        scriptio.add_log_file_handler(args.log_file)

    if args.selected_flags is not None:
        args.selected_flags = args.selected_flags.split(",")

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

    FHC, filter_output_fun = qual.get_qual_filter_handler(
        cid, fmt, args.filter_qual_output, args.compress_level, args.temp_dir
    )

    matcher = FastxMatcher(regex.compile(args.pattern))
    trimmer = get_fastx_trimmer(fmt)
    flag_extractor = flag.get_flag_extractor(fmt, args)
    quality_flag_filters, filter_fun = qual.setup_qual_filters(
        args.filter_qual_flags, args.phred_offset
    )

    filtered_counter = 0
    for record in chunk:
        match, matched = matcher.match(record)
        if matched:
            flags = flag_extractor.extract_all(record, match)
            flags_selected = flag_extractor.apply_selection(flags)
            record = flag_extractor.update(record, flags_selected)
            record = trimmer.trim_re(record, match)
            pass_filters = filter_fun(flags, quality_flag_filters)
            if not pass_filters:
                filtered_counter += 1
                filter_output_fun(record)
                continue
        foutput[matched](record)

    SimpleFastxWriter.close_handle(OHC)
    SimpleFastxWriter.close_handle(UHC)
    SimpleFastxWriter.close_handle(FHC)

    return (filtered_counter, matcher.matched_count, len(chunk))


def run(args: argparse.Namespace) -> None:
    ap.log_args(args)

    fmt, IH = scriptio.get_input_handler(
        args.input, args.compress_level, args.chunk_size
    )

    quality_flag_filters, filter_fun = qual.setup_qual_filters(
        args.filter_qual_flags, args.phred_offset, verbose=True
    )

    logging.info("Trimming and extracting flags...")
    output = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(
            chunk,
            cid,
            args,
        )
        for chunk, cid in IH
    )

    parsed_counter = 0
    matched_counter = 0
    filtered_counter = 0
    for filtered, matched, parsed in output:
        filtered_counter += filtered
        matched_counter += matched
        parsed_counter += parsed
    logging.info(f"{matched_counter}/{parsed_counter} records matched the pattern.")
    if args.filter_qual_output is not None:
        logging.info(
            f"{filtered_counter}/{matched_counter} records passed the quality filters."
        )

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir)
    merger.do(args.output, IH.last_chunk_id, "Matched")
    if args.unmatched_output is not None:
        merger.do(args.unmatched_output, IH.last_chunk_id, "Unmatched")
    if args.filter_qual_output is not None:
        merger.do(args.filter_qual_output, IH.last_chunk_id, "Filtered")

    logging.info("Done. :thumbs_up: :smiley:")
