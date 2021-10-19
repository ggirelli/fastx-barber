"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import io
import os
import shutil
import tempfile


def test_check_tmp_dir():
    path = io.check_tmp_dir()
    if not os.path.isdir(path):
        raise AssertionError
    shutil.rmtree(path)


def test_is_gzipped():
    if not io.is_gzipped("test.txt.gz")[2]:
        raise AssertionError
    if io.is_gzipped("test.txt")[2]:
        raise AssertionError


def test_splitext():
    base, ext = io.splitext("/root/test.txt")
    if base != "/root/test":
        raise AssertionError
    if ext != ".txt":
        raise AssertionError
    base, ext = io.splitext("/root/test.txt.gz")
    if base != "/root/test":
        raise AssertionError
    if ext != ".txt.gz":
        raise AssertionError
    base, ext = io.splitext("/root/test.txt.gz.gz")
    if base != "/root/test":
        raise AssertionError
    if ext != ".txt.gz.gz":
        raise AssertionError


def test_ChunkMerger():
    TD = tempfile.TemporaryDirectory()

    with open(os.path.join(TD.name, ".tmp.chunk1.test.txt"), "w+") as C1:
        C1.write("chunk1\n")
    with open(os.path.join(TD.name, ".tmp.chunk2.test.txt"), "w+") as C2:
        C2.write("chunk2\n")
    merger = io.ChunkMerger(TD)
    merger.do("test.txt", 2, "test_description")

    if os.path.isfile(C1.name):
        raise AssertionError

    with open("test.txt", "r+") as MH:
        merged_content = MH.readlines()
        if len(merged_content) != 2:
            raise AssertionError
        if merged_content[0] != "chunk1\n":
            raise AssertionError
        if merged_content[1] != "chunk2\n":
            raise AssertionError
    os.remove(MH.name)

    shutil.rmtree(TD.name)


def test_ChunkMerger_split():
    TD = tempfile.TemporaryDirectory()

    with open(os.path.join(TD.name, "test_split.ASD.tmp.chunk1.test.txt"), "w+") as C:
        C.write("chunk1\n")
    with open(os.path.join(TD.name, "test_split.DSA.tmp.chunk1.test.txt"), "w+") as C:
        C.write("chunk2\n")
    with open(os.path.join(TD.name, "test_split.ASD.tmp.chunk2.test.txt"), "w+") as C:
        C.write("chunk3\n")
    with open(os.path.join(TD.name, "test_split.DSA.tmp.chunk2.test.txt"), "w+") as C:
        C.write("chunk4\n")
    merger = io.ChunkMerger(TD, "test")
    merger.do("test.txt", 2, "test_description")

    if os.path.isfile(C.name):
        raise AssertionError

    with open("test_split.ASD.test.txt", "r+") as MH:
        merged_content = MH.readlines()
        print(merged_content)
        if len(merged_content) != 2:
            raise AssertionError
        if merged_content[0] != "chunk1\n":
            raise AssertionError
        if merged_content[1] != "chunk3\n":
            raise AssertionError
    os.remove(MH.name)

    with open("test_split.DSA.test.txt", "r+") as MH:
        merged_content = MH.readlines()
        print(merged_content)
        if len(merged_content) != 2:
            raise AssertionError
        if merged_content[0] != "chunk2\n":
            raise AssertionError
        if merged_content[1] != "chunk4\n":
            raise AssertionError
    os.remove(MH.name)

    shutil.rmtree(TD.name)


def test_ChunkMerger_noRemove():
    TD = tempfile.TemporaryDirectory()

    with open(os.path.join(TD.name, ".tmp.chunk1.test.txt"), "w+") as C1:
        C1.write("chunk1\n")
    with open(os.path.join(TD.name, ".tmp.chunk2.test.txt"), "w+") as C2:
        C2.write("chunk2\n")
    merger = io.ChunkMerger(TD)
    merger.do_remove = False
    merger.do("test.txt", 2, "test_description")

    if not os.path.isfile(C1.name):
        raise AssertionError

    with open("test.txt", "r+") as MH:
        merged_content = MH.readlines()
        if len(merged_content) != 2:
            raise AssertionError
        if merged_content[0] != "chunk1\n":
            raise AssertionError
        if merged_content[1] != "chunk2\n":
            raise AssertionError
    os.remove(MH.name)

    shutil.rmtree(TD.name)
