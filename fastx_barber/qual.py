"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber.const import DEFAULT_PHRED_OFFSET, QFLAG_START
from fastx_barber.flag import FlagData
import numpy as np  # type: ignore
from typing import Dict, List


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

    __passed: int = 0
    __parsed: int = 0

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
        return self.__passed

    @property
    def parsed(self) -> int:
        return self.__parsed

    def qual_pass_filter(self, qual: str) -> bool:
        """
        Arguments:
            qual {str} -- phred string

        Returns:
            bool -- whether the quality string passes the filter
        """
        has_passed = self.__qual_pass_filter(qual, self.__min_qscore, self.__max_perc)
        self.__passed += has_passed
        self.__parsed += 1
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
