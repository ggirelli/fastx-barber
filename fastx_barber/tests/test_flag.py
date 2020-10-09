"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from fastx_barber import const, flag, match, random, seqio
import regex  # type: ignore
from typing import Dict


def test_FlagStats():
    fs = flag.FlagStats()
    fs.update({const.UT_FLAG_NAME: ("value", 0, 0)})
    assert 0 == fs.get_dataframe(const.UT_FLAG_NAME).shape[0]
    fs = flag.FlagStats(const.UT_FLAG_NAME)
    fs.update({const.UT_FLAG_NAME: ("value", 0, 0)})
    assert 1 == fs.get_dataframe(const.UT_FLAG_NAME).shape[0]


def assert_FastaFlagExtractor_update(
    fe: flag.FastaFlagExtractor,
    record: seqio.SimpleFastxRecord,
    flag_data: Dict[str, const.FlagData],
) -> None:
    expected_name = f"{record[0]}{fe.flag_delim}{fe.flag_delim}{const.UT_FLAG_NAME}"
    expected_name += f"{fe.flag_delim}{flag_data[const.UT_FLAG_NAME][0]}"
    updated_name, updated_seq, updated_qual = fe.update(record, flag_data)
    assert expected_name == updated_name
    assert record[1] == updated_seq
    assert updated_qual is None


def test_FastaFlagExtractor_noSelectedFlags_noStatFlags():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastaFlagExtractor()
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastaFlagExtractor_update(fe, record, flag_data)
        assert const.UT_FLAG_NAME not in fe.extract_selected(record, match_result)
    assert 0 == len(fe.flagstats.keys())


def test_FastaFlagExtractor_noStatFlags():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastaFlagExtractor([const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastaFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        flag_data = fe.extract_selected(record, match_result)
        assert_FastaFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
    assert 0 == len(fe.flagstats.keys())


def test_FastaFlagExtractor():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastaFlagExtractor([const.UT_FLAG_NAME], [const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastaFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        flag_data = fe.extract_selected(record, match_result)
        assert_FastaFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
    assert 1 == len(fe.flagstats.keys())


def test_FastaFlagExtractor_noSelectedFlags():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastaFlagExtractor(None, [const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastaFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        assert const.UT_FLAG_NAME not in fe.extract_selected(record, match_result)
    assert 1 == len(fe.flagstats.keys())


def assert_FastqFlagExtractor_update(
    fe: flag.FastqFlagExtractor,
    record: seqio.SimpleFastxRecord,
    flag_data: Dict[str, const.FlagData],
) -> None:
    expected_name = f"{record[0]}{fe.flag_delim}{fe.flag_delim}{const.UT_FLAG_NAME}"
    expected_name += f"{fe.flag_delim}{flag_data[const.UT_FLAG_NAME][0]}"
    expected_name += f"{fe.flag_delim}{fe.flag_delim}q{const.UT_FLAG_NAME}"
    expected_name += f"{fe.flag_delim}{flag_data['q'+const.UT_FLAG_NAME][0]}"
    updated_name, updated_seq, updated_qual = fe.update(record, flag_data)
    assert expected_name == updated_name
    assert record[1] == updated_seq
    assert record[2] == updated_qual


def test_FastqFlagExtractor_noSelectedFlags_noStatFlags():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastqFlagExtractor()
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastqFlagExtractor_update(fe, record, flag_data)
        assert const.UT_FLAG_NAME not in fe.extract_selected(record, match_result)
    assert 0 == len(fe.flagstats.keys())


def test_FastqFlagExtractor_noStatFlags():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastqFlagExtractor([const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastqFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        assert record[2][:8] == flag_data["q" + const.UT_FLAG_NAME][0]
        flag_data = fe.extract_selected(record, match_result)
        assert_FastqFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        assert record[2][:8] == flag_data["q" + const.UT_FLAG_NAME][0]
    assert 0 == len(fe.flagstats.keys())


def test_FastqFlagExtractor():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastqFlagExtractor([const.UT_FLAG_NAME], [const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastqFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        assert record[2][:8] == flag_data["q" + const.UT_FLAG_NAME][0]
        flag_data = fe.extract_selected(record, match_result)
        assert_FastqFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        assert record[2][:8] == flag_data["q" + const.UT_FLAG_NAME][0]
    assert 1 == len(fe.flagstats.keys())


def test_FastqFlagExtractor_noSelectedFlags():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastqFlagExtractor(None, [const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        assert_FastqFlagExtractor_update(fe, record, flag_data)
        assert record[1][:8] == flag_data[const.UT_FLAG_NAME][0]
        assert record[2][:8] == flag_data["q" + const.UT_FLAG_NAME][0]
        assert const.UT_FLAG_NAME not in fe.extract_selected(record, match_result)
    assert 1 == len(fe.flagstats.keys())


def test_get_fastx_flag_extractor():
    assert (
        flag.get_fastx_flag_extractor(const.FastxFormats.FASTA)
        is flag.FastaFlagExtractor
    )
    assert (
        flag.get_fastx_flag_extractor(const.FastxFormats.FASTQ)
        is flag.FastqFlagExtractor
    )
    assert (
        flag.get_fastx_flag_extractor(const.FastxFormats.NONE) is flag.ABCFlagExtractor
    )


def test_FastxFlagReader_fasta():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fasta_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastaFlagExtractor(None, [const.UT_FLAG_NAME])
    fr = flag.FastxFlagReader([const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        updated_record = fe.update(record, flag_data)
        read_flag_data = fr.read(updated_record)
        for k, v in flag_data.items():
            assert k in read_flag_data
            assert read_flag_data[k][0] == v[0]
        assert list(fe.flagstats.items()) == list(fr.flagstats.items())


def test_FastxFlagReader_fastq():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    generated_records = random.make_fastq_file(
        const.UT_N_RECORDS, const.UT_RECORD_SEQ_LEN
    )
    fe = flag.FastqFlagExtractor(None, [const.UT_FLAG_NAME])
    fr = flag.FastxFlagReader([const.UT_FLAG_NAME])
    for record in generated_records:
        match_result, matched = matcher.do(record)
        flag_data = fe.extract_all(record, match_result)
        fe.update_stats(flag_data)
        updated_record = fe.update(record, flag_data)
        read_flag_data = fr.read(updated_record)
        for k, v in flag_data.items():
            assert k in read_flag_data
            assert read_flag_data[k][0] == v[0]
        assert list(fe.flagstats.items()) == list(fr.flagstats.items())


def test_FlagRegexes_fasta():
    matcher = match.FastxMatcher(regex.compile(const.UT_FLAG_PATTERN))
    fe = flag.FastaFlagExtractor([const.UT_FLAG_NAME])
    record = ("fake", "ATCGATCGATCGATCGAT", None)
    match_result, matched = matcher.do(record)
    flag_data = fe.extract_all(record, match_result)
    fr = flag.FlagRegexes([f"{const.UT_FLAG_NAME},^AT.{{6}}$"])
    assert fr.match(flag_data)
    fr = flag.FlagRegexes([f"{const.UT_FLAG_NAME},^GT.{{6}}$"])
    assert not fr.match(flag_data)
