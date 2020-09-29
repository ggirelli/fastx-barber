[![DOI](https://zenodo.org/badge/281703558.svg)](https://zenodo.org/badge/latestdoi/281703558)

A Python3.6.1+ package to trim and extract flags from FASTA  and FASTQ files.

## Features

* Works on both FASTA and FASTQ files.
* Selects reads based on a pattern (regex).
* Trims reads by pattern (regex), length, or quality (base-wise).
* Extracts parts (flags) of reads based on a pattern, and stores them in the read headers.
    - Optionally extracts the corresponding portions of the quality string (only for fastq files).
    - Optionally filters based on quality score of extracted flags (only for fastq files).
        + Supports Sanger QSCORE definition (not old Solexa/Illumina one).
        + Supports custom PHRED offset.
        + Optionally exports reads that do not pass the specified filters.
    - Optionally split output based on flag value.
    - Optionally calculates the frequency of each value of a set of flags (flagstats).
    - Filtering by flag quality, splitting by flag value, and flag value frequency features are available also as separate scripts to be applied to files with previously extracted flags.
* Filters a FASTX file with extracted flags by applying patterns to different flags.
* Regular expression support [*fuzzy* matching](https://pypi.org/project/regex/#approximate-fuzzy-matching-hg-issue-12-hg-issue-41-hg-issue-109) (*fuzzy matching* might affect the barber's speed).
    * Optionally exports reads that do not match the provided pattern(s).
* Parallelizes processing by splitting the fastx file in chunks.

## Requirements

`fastx-barber` has been tested with Python 3.6.1, 3.7, and 3.8. We recommend installing it using `pipx` (see [below](https://github.com/ggirelli/fastx-barber#install)) to avoid dependency conflicts with other packages. The packages it depends on are listed in our [dependency graph](https://github.com/ggirelli/fastx-barber/network/dependencies). We use [`poetry`](https://github.com/python-poetry/poetry) to handle our dependencies.

## Install

We recommend installing `fastx-barber` using [`pipx`](https://github.com/pipxproject/pipx). Check how to install `pipx` [here](https://github.com/pipxproject/pipx#install-pipx) if you don't have it yet!

Once you have `pipx` ready on your system, install the latest stable release of `fastx-barber` by running: `pipx install fastx-barber`. If you see the stars (✨ 🌟 ✨), then the installation went well!

## Usage

Run:

* `fbarber` to access the barber's services.
* `fbarber flag` to extract or manipulate read flags.
* `fbarber match` to select reads based on a pattern (regular expression).
* `fbarber trim` to trim your reads.

Add `-h` to see the full help page of a command!

## Contributing

We welcome any contributions to `fastx-barber`. In short, we use [`black`](https://github.com/psf/black) to standardize code format. Any code change also needs to pass `mypy` checks. For more details, please refer to our [contribution guidelines](https://github.com/ggirelli/fastx-barber/blob/master/CONTRIBUTING.md) if this is your first time contributing! Also, check out our [code of conduct](https://github.com/ggirelli/fastx-barber/blob/master/CODE_OF_CONDUCT.md).

## License

`MIT License - Copyright (c) 2020 Gabriele Girelli`
