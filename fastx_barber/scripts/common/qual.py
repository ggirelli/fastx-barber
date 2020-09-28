"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.const import FastxFormats
from fastx_barber.qual import dummy_apply_filter_flag, apply_filter_flag, QualityFilter
from fastx_barber.seqio import (
    SimpleFastxWriter,
)
from fastx_barber.scripts.common.io import get_chunk_handler
import logging
import tempfile
from typing import Callable, Dict, Optional, Tuple


def setup_qual_filters(
    filter_qual_flags: str, phred_offset: int, verbose: bool = False
) -> Tuple[Dict[str, QualityFilter], Callable]:
    quality_flag_filters: Dict[str, QualityFilter] = {}
    filter_fun = dummy_apply_filter_flag
    if filter_qual_flags is not None:
        quality_flag_filters = QualityFilter.init_flag_filters(
            filter_qual_flags.split(" "), phred_offset
        )
        if verbose:
            logging.info(f"[bold underline green]PHRED offset[/]\t{phred_offset}")
            for name, f in quality_flag_filters.items():
                logging.info(
                    "".join(
                        (
                            f"[bold underline green]{name}-filter[/]",
                            f"\tmin_score={f.min_qscore}",
                            f"\n\t\tmax_perc={f.max_perc}",
                        )
                    )
                )
        filter_fun = apply_filter_flag
    return (quality_flag_filters, filter_fun)


def get_qual_filter_handler(
    cid: int,
    fmt: FastxFormats,
    path: Optional[str],
    compress_level: int,
    tempdir: Optional[tempfile.TemporaryDirectory] = None,
) -> Tuple[Optional[SimpleFastxWriter], Callable]:
    FH = get_chunk_handler(cid, fmt, path, compress_level, tempdir)
    if FH is not None:
        assert fmt == FH.format, "format mismatch between input and requested output"
        return (FH, FH.write)
    else:
        return (FH, lambda x: None)
