"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import io
from fastx_barber.const import BedExtension, BedRecord
import gzip
from typing import IO


class BedWriter(object):
    _OH: IO
    _n_fields: int
    __closed: bool

    def __init__(self, path: str, n_fields: int):
        super(BedWriter, self).__init__()
        base, ext, gzipped = io.is_gzipped(path)
        assert ext == BedExtension
        assert n_fields in [3, 4, 5, 6, 12]
        if gzipped:
            self._OH = gzip.open(path, "wt")
        else:
            self._OH = open(path, "w+")
        self.__closed = False
        self._n_fields = n_fields

    def __write_bed_record(self, record: BedRecord, n_fields: int):
        assert len(record) >= n_fields
        self._OH.write(f"{record[0]}")
        for i in range(1, n_fields):
            self._OH.write(f"\t{record[i]}")
        self._OH.write("\n")

    def do(self, record: BedRecord) -> None:
        assert not self.__closed
        self.__write_bed_record(record, self._n_fields)

    def close(self):
        self._OH.close()
        self.__closed = True
