"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.const import DEFAULT_PHRED_OFFSET, FlagData, QFLAG_START
import logging
import numpy as np  # type: ignore
from typing import Callable, Dict, List, Tuple


class QualityIO(object):
    """docstring for QualityIO"""

    __phred_offset: int

    def __init__(self, phred_offset: int = 33):
        super(QualityIO, self).__init__()
        assert phred_offset in [33, 64]
        self.__phred_offset = phred_offset

    @property
    def phred_offset(self) -> int:
        return self.__phred_offset

    def phred_to_qscore(self, qual: str) -> List[int]:
        qscore = [ord(c) - self.__phred_offset for c in qual]
        assert not any(
            [q < 0 for q in qscore]
        ), f"phred offset of {self.__phred_offset} produces negative qscores"
        return qscore


class QualityFilter(QualityIO):
    """docstring for QualityFilter"""

    __min_qscore: int
    __max_perc: float

    _passed: int = 0
    _parsed: int = 0

    def __init__(
        self, min_qscore: int, max_perc: float, phred_offset: int = DEFAULT_PHRED_OFFSET
    ):
        super(QualityFilter, self).__init__(phred_offset)
        self.min_qscore = min_qscore
        self.max_perc = max_perc

    @property
    def min_qscore(self) -> int:
        return self.__min_qscore

    @min_qscore.setter
    def min_qscore(self, min_qscore: int) -> None:
        self.__min_qscore = min_qscore

    @property
    def max_perc(self) -> float:
        return self.__max_perc

    @max_perc.setter
    def max_perc(self, max_perc: float) -> None:
        assert max_perc >= 0 and max_perc <= 1
        self.__max_perc = max_perc

    @property
    def passed(self) -> int:
        return self._passed

    @property
    def parsed(self) -> int:
        return self._parsed

    def qual_pass_filter(self, qual: str) -> bool:
        """
        Arguments:
            qual {str} -- phred string

        Returns:
            bool -- whether the quality string passes the filter
        """
        has_passed = self.__qual_pass_filter(qual, self.__min_qscore, self.__max_perc)
        self._passed += has_passed
        self._parsed += 1
        return has_passed

    def __qual_pass_filter(self, qual: str, min_qscore: int, max_perc: float) -> bool:
        """
        Arguments:
            qual {str} -- phred string
            min_qscore {int} -- qscore threshold (lower qscores considered low quality)
            max_perc {float} -- max fraction (inclusive) of low quality bases
                                to pass the filter

        Returns:
            bool -- whether the quality string passes the filter
        """
        qscore = np.array(self.phred_to_qscore(qual))
        low_quality_fraction = (qscore < min_qscore).sum() / len(qual)
        return low_quality_fraction <= max_perc

    @staticmethod
    def init_flag_filters(
        filters: List[str], phred_offset: int
    ) -> Dict[str, "QualityFilter"]:
        filter_dict: Dict[str, QualityFilter] = {}
        for f in filters:
            flag, min_qscore_str, max_perc_str = f.split(",")
            min_qscore = int(min_qscore_str)
            max_perc = float(max_perc_str)
            filter_dict[f"{QFLAG_START}{flag}"] = QualityFilter(
                min_qscore, max_perc, phred_offset
            )
        return filter_dict


def dummy_apply_filter_flag(
    flag_data: Dict[str, FlagData], filters: Dict[str, QualityFilter]
) -> bool:
    return True


def apply_filter_flag(
    flag_data: Dict[str, FlagData], filters: Dict[str, QualityFilter]
) -> bool:
    """
    Arguments:
        flag_data {Dict[str, FlagData]} -- dict with flag name as key and data as value
        filters: {Dict[str, QualityFilter]} -- dict with flag name as key
                                               and filter as value

    Returns:
        bool -- whether the flags pass the filters
    """
    for flag, (qual, start, end) in flag_data.items():
        if not flag.startswith(QFLAG_START) or flag not in filters.keys():
            continue
        if not filters[flag].qual_pass_filter(qual):
            return False
    return True


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
