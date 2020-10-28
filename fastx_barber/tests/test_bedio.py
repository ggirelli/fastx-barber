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
        assert len(bed_data) == len(bed_content)
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            assert 3 == len(record)
            assert bed_data[i][0] == record[0]
            assert bed_data[i][1] == int(record[1])
            assert bed_data[i][2] == int(record[2])

    os.remove(bed_path)


def test_BedWriter_4fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 4)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        assert len(bed_data) == len(bed_content)
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            assert 4 == len(record)
            assert bed_data[i][0] == record[0]
            assert bed_data[i][1] == int(record[1])
            assert bed_data[i][2] == int(record[2])
            assert bed_data[i][3] == record[3]

    os.remove(bed_path)


def test_BedWriter_5fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 5)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        assert len(bed_data) == len(bed_content)
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            assert 5 == len(record)
            assert bed_data[i][0] == record[0]
            assert bed_data[i][1] == int(record[1])
            assert bed_data[i][2] == int(record[2])
            assert bed_data[i][3] == record[3]
            assert bed_data[i][4] == float(record[4])

    os.remove(bed_path)


def test_BedWriter_6fields():
    bed_path = "test.bed"
    bw = bedio.BedWriter(bed_path, 6)
    for record in bed_data:
        bw.do(record)
    bw.close()

    with open(bed_path) as IH:
        bed_content = IH.readlines()
        assert len(bed_data) == len(bed_content)
        for i in range(len(bed_data)):
            record = bed_content[i].strip().split()
            assert 6 == len(record)
            assert bed_data[i][0] == record[0]
            assert bed_data[i][1] == int(record[1])
            assert bed_data[i][2] == int(record[2])
            assert bed_data[i][3] == record[3]
            assert bed_data[i][4] == float(record[4])
            assert bed_data[i][5] == record[5]

    os.remove(bed_path)
