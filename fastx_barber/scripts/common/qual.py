"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.const import FastxFormats
from fastx_barber.qual import dummy_apply_filter_flag, apply_filter_flag, QualityFilter
from fastx_barber.scripts.common import io as scriptio
from fastx_barber.seqio import (
    SimpleFastxWriter,
    SimpleSplitFastxWriter,
)
import logging
import tempfile
from typing import Callable, Dict, List, Optional, Tuple


def log_qual_filters(
    phred_offset: int, quality_flag_filters: Dict[str, QualityFilter]
) -> None:
    logging.info("[bold underline red]Quality filters[/]")
    logging.info(f"PHRED offset\t{phred_offset}")
    for name, f in quality_flag_filters.items():
        logging.info(f"{name}-filter\tmin_score={f.min_qscore} & max_perc={f.max_perc}")


def setup_qual_filters(
    filter_qual_flags: List[str], phred_offset: int, verbose: bool = False
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
        return (FH, lambda *x: None)


def get_split_qual_filter_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    split_by: str,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Tuple[Optional[SimpleSplitFastxWriter], Callable]:
    FH = scriptio.get_split_chunk_handler(
        cid, fmt, path, compress_level, split_by, tempdir
    )
    if FH is not None:
        assert fmt == FH.format, "format mismatch between input and requested output"
        return (FH, FH.write)
    else:
        return (FH, lambda *x: None)
