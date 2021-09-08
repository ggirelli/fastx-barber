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
    assert os.path.isdir(path)
    shutil.rmtree(path)


def test_is_gzipped():
    assert io.is_gzipped("test.txt.gz")[2]
    assert not io.is_gzipped("test.txt")[2]


def test_splitext():
    base, ext = io.splitext("/root/test.txt")
    assert "/root/test" == base
    assert ".txt" == ext
    base, ext = io.splitext("/root/test.txt.gz")
    assert "/root/test" == base
    assert ".txt.gz" == ext
    base, ext = io.splitext("/root/test.txt.gz.gz")
    assert "/root/test" == base
    assert ".txt.gz.gz" == ext


def test_ChunkMerger():
    TD = tempfile.TemporaryDirectory()

    with open(os.path.join(TD.name, ".tmp.chunk1.test.txt"), "w+") as C1:
        C1.write("chunk1\n")
    with open(os.path.join(TD.name, ".tmp.chunk2.test.txt"), "w+") as C2:
        C2.write("chunk2\n")
    merger = io.ChunkMerger(TD)
    merger.do("test.txt", 2, "test_description")

    assert not os.path.isfile(C1.name)

    with open("test.txt", "r+") as MH:
        merged_content = MH.readlines()
        assert 2 == len(merged_content)
        assert "chunk1\n" == merged_content[0]
        assert "chunk2\n" == merged_content[1]
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

    assert not os.path.isfile(C.name)

    with open("test_split.ASD.test.txt", "r+") as MH:
        merged_content = MH.readlines()
        print(merged_content)
        assert 2 == len(merged_content)
        assert "chunk1\n" == merged_content[0]
        assert "chunk3\n" == merged_content[1]
    os.remove(MH.name)

    with open("test_split.DSA.test.txt", "r+") as MH:
        merged_content = MH.readlines()
        print(merged_content)
        assert 2 == len(merged_content)
        assert "chunk2\n" == merged_content[0]
        assert "chunk4\n" == merged_content[1]
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

    assert os.path.isfile(C1.name)

    with open("test.txt", "r+") as MH:
        merged_content = MH.readlines()
        assert 2 == len(merged_content)
        assert "chunk1\n" == merged_content[0]
        assert "chunk2\n" == merged_content[1]
    os.remove(MH.name)

    shutil.rmtree(TD.name)
