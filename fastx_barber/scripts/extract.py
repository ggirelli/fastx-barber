"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from collections import defaultdict
from fastx_barber.const import DEFAULT_PHRED_OFFSET, FastxFormats
from fastx_barber.flag import (
    FlagStats,
    get_fastx_flag_extractor,
    ABCFlagExtractor,
    FastqFlagExtractor,
)
from fastx_barber.io import ChunkMerger
from fastx_barber.match import FastxMatcher
from fastx_barber.qual import dummy_apply_filter_flag, apply_filter_flag, QualityFilter
from fastx_barber.scripts.common import arguments as ap
from fastx_barber.scripts.common import io as scriptio
from fastx_barber.seqio import get_fastx_format, SimpleFastxRecord, SimpleFastxWriter
from fastx_barber.trim import get_fastx_trimmer
import joblib  # type: ignore
import logging
import os
import pandas as pd  # type: ignore
import regex  # type: ignore
from rich.logging import RichHandler
from rich.progress import track
import tempfile
from typing import Callable, Dict, List, Optional, Tuple

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
        nargs="+",
        help="""Space-separate names of flags to be extracted.
        By default it extracts all flags.""",
    )
    advanced.add_argument(
        "--flagstats",
        type=str,
        nargs="+",
        help="""Space-separate names of flags to calculate statistics for. By default
        this is skipped. Statistics are calculated before any quality filter, on records
        matching the provided pattern.""",
    )
    advanced.add_argument(
        "--filter-qual-flags",
        type=str,
        nargs="+",
        help="""Space-separated 'flag_name,min_qscore,max_perc' strings, where
        bases with qscore < min_qscore are considered low quality, and max_perc
        is the largest allowed fraction of low quality bases. I.e., you can specify
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

    ap.log_args(args)
    logging.info("[bold underline red]Flag extraction[/]")
    if args.selected_flags is not None:
        logging.info(f"Selected flags\t{args.selected_flags}")
    logging.info(f"Flag stats\t{args.flagstats}")
    logging.info(f"Flag delim\t'{args.flag_delim}'")
    logging.info(f"Comment delim\t'{args.comment_space}'")
    logging.info(f"Quality flags\t{args.qual_flags}")

    return args


def log_qual_filters(
    phred_offset: int, quality_flag_filters: Dict[str, QualityFilter]
) -> None:
    logging.info("[bold underline red]Quality filters[/]")
    logging.info(f"PHRED offset\t{phred_offset}")
    for name, f in quality_flag_filters.items():
        logging.info(f"{name}-filter\tmin_score={f.min_qscore} & max_perc={f.max_perc}")


def setup_qual_filters(
    filter_qual_flags: str, phred_offset: int, verbose: bool = False
) -> Tuple[Dict[str, QualityFilter], Callable]:
    quality_flag_filters: Dict[str, QualityFilter] = {}
    filter_fun = dummy_apply_filter_flag
    if filter_qual_flags is not None:
        quality_flag_filters = QualityFilter.init_flag_filters(
            filter_qual_flags, phred_offset
        )
        if verbose:
            log_qual_filters(phred_offset, quality_flag_filters)
        filter_fun = apply_filter_flag
    return (quality_flag_filters, filter_fun)


def get_qual_filter_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Tuple[Optional[SimpleFastxWriter], Callable]:
    FH = scriptio.get_chunk_handler(cid, fmt, path, compress_level, tempdir)
    if FH is not None:
        assert fmt == FH.format, "format mismatch between input and requested output"
        return (FH, FH.write)
    else:
        return (FH, lambda x: None)


def get_flag_extractor(fmt: FastxFormats, args: argparse.Namespace) -> ABCFlagExtractor:
    flag_extractor = get_fastx_flag_extractor(fmt)(args.selected_flags, args.flagstats)
    flag_extractor.flag_delim = args.flag_delim
    flag_extractor.comment_space = args.comment_space
    if isinstance(flag_extractor, FastqFlagExtractor):
        flag_extractor.extract_qual_flags = args.qual_flags
    return flag_extractor


ChunkDetails = Tuple[int, int, int, FlagStats]


def run_chunk(
    chunk: List[SimpleFastxRecord],
    cid: int,
    args: argparse.Namespace,
) -> ChunkDetails:
    fmt, _ = get_fastx_format(args.input)
    OHC = scriptio.get_chunk_handler(
        cid, fmt, args.output, args.compress_level, args.temp_dir
    )
    assert OHC is not None
    UHC = scriptio.get_chunk_handler(
        cid, fmt, args.unmatched_output, args.compress_level, args.temp_dir
    )
    foutput = scriptio.get_output_fun(OHC, UHC)

    FHC, filter_output_fun = get_qual_filter_handler(
        cid, fmt, args.filter_qual_output, args.compress_level, args.temp_dir
    )

    matcher = FastxMatcher(regex.compile(args.pattern))
    trimmer = get_fastx_trimmer(fmt)
    flag_extractor = get_flag_extractor(fmt, args)
    quality_flag_filters, filter_fun = setup_qual_filters(
        args.filter_qual_flags, args.phred_offset
    )

    filtered_counter = 0
    for record in chunk:
        match, matched = matcher.match(record)
        if matched:
            flags = flag_extractor.extract_all(record, match)
            flag_extractor.update_stats(flags)
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

    return (
        filtered_counter,
        matcher.matched_count,
        len(chunk),
        flag_extractor.flagstats,
    )


def merge_chunk_details(chunk_details: ChunkDetails) -> ChunkDetails:
    parsed_counter = 0
    matched_counter = 0
    filtered_counter = 0
    flagstats: FlagStats = defaultdict(lambda: defaultdict(lambda: 0))
    for filtered, matched, parsed, stats in chunk_details:
        filtered_counter += filtered
        matched_counter += matched
        parsed_counter += parsed
        for flag_name, data in stats.items():
            for k, v in data.items():
                flagstats[flag_name][k] += v

    return (parsed_counter, matched_counter, filtered_counter, flagstats)


def export_flagstats(flagstats: FlagStats, output_path: str) -> None:
    output_dir = os.path.dirname(output_path)
    basename = os.path.basename(output_path)
    if basename.endswith(".gz"):
        basename = basename.split(".gz")[0]
    basename = os.path.splitext(basename)[0]
    for flag_name, stats in track(flagstats.items(), description="Exporting flagstats"):
        df = pd.DataFrame()
        df["value"] = list(stats.keys())
        df["counts"] = list(stats.values())
        df["perc"] = round(df["counts"] / df["counts"].sum() * 100, 2)
        df.sort_values("perc", ascending=False, ignore_index=True, inplace=True)
        df.to_csv(
            os.path.join(output_dir, f"{basename}.{flag_name}.stats.tsv"),
            sep="\t",
            index=False,
        )


def run(args: argparse.Namespace) -> None:
    fmt, IH = scriptio.get_input_handler(
        args.input, args.compress_level, args.chunk_size
    )

    quality_flag_filters, filter_fun = setup_qual_filters(
        args.filter_qual_flags, args.phred_offset, verbose=True
    )

    logging.info("[bold underline red]Running[/]")
    logging.info("Trimming and extracting flags...")
    chunk_details = joblib.Parallel(n_jobs=args.threads, verbose=10)(
        joblib.delayed(run_chunk)(
            chunk,
            cid,
            args,
        )
        for chunk, cid in IH
    )
    logging.info("Merging subprocesses details...")
    n_parsed, n_matched, n_filtered, flagstats = merge_chunk_details(chunk_details)

    logging.info(
        f"{n_matched}/{n_parsed} ({n_matched/n_parsed*100:.2f}%) "
        + "records matched the pattern.",
    )
    if args.filter_qual_flags is not None:
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
        export_flagstats(flagstats, args.output)

    logging.info("Merging batch output...")
    merger = ChunkMerger(args.temp_dir)
    merger.do(args.output, IH.last_chunk_id, "Writing matched records")
    if args.unmatched_output is not None:
        merger.do(args.unmatched_output, IH.last_chunk_id, "Writing unmatched records")
    if args.filter_qual_output is not None:
        merger.do(args.filter_qual_output, IH.last_chunk_id, "Writing filtered records")

    logging.info("Done. :thumbs_up: :smiley:")
