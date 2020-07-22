'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

from Bio.SeqRecord import SeqRecord


class FastxTrimmer(object):
    """Trimming class for fasta and fastq files"""
    def __init__(self, pattern: str, fmt: str):
        super(FastxTrimmer, self).__init__()
        self._pattern = pattern
        assert fmt in ['fasta', 'fastq']
        self.__fmt = fmt

    def trim(self, record: SeqRecord) -> None:
        if "fasta" == self.__fmt:
            self._trim_fasta(record)
        elif "fastq" == self.__fmt:
            self._trim_fastq(record)

    def _trim_fastq(self, record: SeqRecord) -> None:
        print(f"\nTrimming fastq:\n{record}")

    def _trim_fasta(self, record: SeqRecord) -> None:
        print(f"\nTrimming fasta:\n{record}")


class FastaTrimmer(FastxTrimmer):
    """Alias for FastxTrimmer(fmt="fasta")"""
    def __init__(self, pattern: str):
        super(FastaTrimmer, self).__init__(pattern)

    def trim(self, record: SeqRecord) -> None:
        self._trim_fasta(record)


class FastqTrimmer(FastxTrimmer):
    """Alias for FastxTrimmer(fmt="fastq")"""
    def __init__(self, pattern: str):
        super(FastqTrimmer, self).__init__(pattern)

    def trim(self, record: SeqRecord) -> None:
        self._trim_fastq(record)
