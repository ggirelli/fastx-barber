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

    C1 = open(os.path.join(TD.name, ".tmp.chunk1.test.txt"), "w+")
    C1.write("chunk1\n")
    C1.close()

    C2 = open(os.path.join(TD.name, ".tmp.chunk2.test.txt"), "w+")
    C2.write("chunk2\n")
    C2.close()

    merger = io.ChunkMerger(TD)
    merger.do("test.txt", 2, "test_description")

    assert not os.path.isfile(C1.name)

    MH = open("test.txt", "r+")
    merged_content = MH.readlines()
    assert 2 == len(merged_content)
    assert "chunk1\n" == merged_content[0]
    assert "chunk2\n" == merged_content[1]
    MH.close()
    os.remove(MH.name)

    shutil.rmtree(TD.name)


def test_ChunkMerger_split():
    TD = tempfile.TemporaryDirectory()

    C = open(os.path.join(TD.name, "test_split.ASD.tmp.chunk1.test.txt"), "w+")
    C.write("chunk1\n")
    C.close()

    C = open(os.path.join(TD.name, "test_split.DSA.tmp.chunk1.test.txt"), "w+")
    C.write("chunk2\n")
    C.close()

    C = open(os.path.join(TD.name, "test_split.ASD.tmp.chunk2.test.txt"), "w+")
    C.write("chunk3\n")
    C.close()

    C = open(os.path.join(TD.name, "test_split.DSA.tmp.chunk2.test.txt"), "w+")
    C.write("chunk4\n")
    C.close()

    merger = io.ChunkMerger(TD, "test")
    merger.do("test.txt", 2, "test_description")

    assert not os.path.isfile(C.name)

    MH = open("test_split.ASD.test.txt", "r+")
    merged_content = MH.readlines()
    print(merged_content)
    assert 2 == len(merged_content)
    assert "chunk1\n" == merged_content[0]
    assert "chunk3\n" == merged_content[1]
    MH.close()
    os.remove(MH.name)

    MH = open("test_split.DSA.test.txt", "r+")
    merged_content = MH.readlines()
    print(merged_content)
    assert 2 == len(merged_content)
    assert "chunk2\n" == merged_content[0]
    assert "chunk4\n" == merged_content[1]
    MH.close()
    os.remove(MH.name)

    shutil.rmtree(TD.name)


def test_ChunkMerger_noRemove():
    TD = tempfile.TemporaryDirectory()

    C1 = open(os.path.join(TD.name, ".tmp.chunk1.test.txt"), "w+")
    C1.write("chunk1\n")
    C1.close()

    C2 = open(os.path.join(TD.name, ".tmp.chunk2.test.txt"), "w+")
    C2.write("chunk2\n")
    C2.close()

    merger = io.ChunkMerger(TD)
    merger.do_remove = False
    merger.do("test.txt", 2, "test_description")

    assert os.path.isfile(C1.name)

    MH = open("test.txt", "r+")
    merged_content = MH.readlines()
    assert 2 == len(merged_content)
    assert "chunk1\n" == merged_content[0]
    assert "chunk2\n" == merged_content[1]
    MH.close()
    os.remove(MH.name)

    shutil.rmtree(TD.name)
