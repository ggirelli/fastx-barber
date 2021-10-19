"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import bedio
import os

bed_data = [
    ("chr1", 1, 10, "row1", 3.0, "+", None, None, None, None, None, None),
    ("chr1", 12, 102, "row2", 5.0, "-", None, None, None, None, None, None),
    ("chr4", 10, 12, "row3", 3.7, "+", None, None, None, None, None, None),
]


def test_BedWriter_3fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 3)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        if len(bed_data) != len(bed_content):
            raise AssertionError
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            if 3 != len(record):
                raise AssertionError
            if bed_data[i][0] != record[0]:
                raise AssertionError
            if bed_data[i][1] != int(record[1]):
                raise AssertionError
            if bed_data[i][2] != int(record[2]):
                raise AssertionError

    os.remove(bed_path)


def test_BedWriter_4fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 4)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        if len(bed_data) != len(bed_content):
            raise AssertionError
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            if 4 != len(record):
                raise AssertionError
            if bed_data[i][0] != record[0]:
                raise AssertionError
            if bed_data[i][1] != int(record[1]):
                raise AssertionError
            if bed_data[i][2] != int(record[2]):
                raise AssertionError
            if bed_data[i][3] != record[3]:
                raise AssertionError

    os.remove(bed_path)


def test_BedWriter_5fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 5)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        if len(bed_data) != len(bed_content):
            raise AssertionError
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            if 5 != len(record):
                raise AssertionError
            if bed_data[i][0] != record[0]:
                raise AssertionError
            if bed_data[i][1] != int(record[1]):
                raise AssertionError
            if bed_data[i][2] != int(record[2]):
                raise AssertionError
            if bed_data[i][3] != record[3]:
                raise AssertionError
            if bed_data[i][4] != float(record[4]):
                raise AssertionError

    os.remove(bed_path)


def test_BedWriter_6fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 6)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        if len(bed_data) != len(bed_content):
            raise AssertionError
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            if 6 != len(record):
                raise AssertionError
            if bed_data[i][0] != record[0]:
                raise AssertionError
            if bed_data[i][1] != int(record[1]):
                raise AssertionError
            if bed_data[i][2] != int(record[2]):
                raise AssertionError
            if bed_data[i][3] != record[3]:
                raise AssertionError
            if bed_data[i][4] != float(record[4]):
                raise AssertionError
            if bed_data[i][5] != record[5]:
                raise AssertionError

    os.remove(bed_path)
