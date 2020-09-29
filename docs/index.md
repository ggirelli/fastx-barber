<!-- MarkdownTOC -->

- [Requirements](#requirements)
- [Install](#install)
- [Features](#features)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

<!-- /MarkdownTOC -->

---

[![DOI](https://zenodo.org/badge/281703558.svg)](https://zenodo.org/badge/latestdoi/281703558) ![](https://img.shields.io/librariesio/github/ggirelli/fastx-barber.svg?style=flat) ![](https://img.shields.io/github/license/ggirelli/fastx-barber.svg?style=flat) ![Test](https://github.com/ggirelli/fastx-barber/workflows/Python%20package/badge.svg?branch=master&event=push)  
![](https://img.shields.io/github/release/ggirelli/fastx-barber.svg?style=flat) ![](https://img.shields.io/github/release-date/ggirelli/fastx-barber.svg?style=flat) ![](https://img.shields.io/github/languages/code-size/ggirelli/fastx-barber.svg?style=flat)  
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastx-barber) ![PyPI - Format](https://img.shields.io/pypi/format/fastx-barber) ![PyPI - Status](https://img.shields.io/pypi/status/fastx-barber)  
![](https://img.shields.io/github/watchers/ggirelli/fastx-barber.svg?label=Watch&style=social) ![](https://img.shields.io/github/stars/ggirelli/fastx-barber.svg?style=social)

A Python3.6.1+ package to trim and extract flags from FASTA  and FASTQ files.

## Requirements

`fastx-barber` has been tested with Python 3.6.1, 3.7, and 3.8. We recommend installing it using `pipx` (see [below](#install)) to avoid dependency conflicts with other packages. The packages it depends on are listed in our [dependency graph](https://github.com/ggirelli/fastx-barber/network/dependencies). We use [`poetry`](https://github.com/python-poetry/poetry) to handle our dependencies.

## Install

We recommend installing `fastx-barber` using [`pipx`](https://github.com/pipxproject/pipx). Check how to install `pipx` [here](https://github.com/pipxproject/pipx#install-pipx) if you don't have it yet! Once you have `pipx` ready on your system, install the latest stable release of `fastx-barber` by running: `pipx install fastx-barber`. If you see the stars (✨ 🌟 ✨), then the installation went well!

## Features

* Works on both FASTA and FASTQ files.
* [Selects](usage#match) reads based on a pattern (regex).
* [Trims](usage#trim) reads [by pattern](usage#trim-by-regular-expression) (regex), [length](usage#trim-by-length), or single-base [quality](usage#trim-by-quality).
* [Extracts](usage#extract-flags) parts ([flags](usage#flags)) of reads based on a pattern, and stores them in the read headers.
    - Optionally extracts the corresponding portions of the quality string (only for fastq files).
    - Optionally filters based on quality score of extracted flags (only for fastq files).
        + Supports Sanger QSCORE definition (not old Solexa/Illumina one).
        + Supports custom PHRED offset.
        + Optionally exports reads that do not pass the specified filters.
    - Optionally split output based on flag value.
    - Optionally calculates the frequency of each value of a set of flags (flagstats).
    - [Filtering by flag quality](usage#filter-by-flag-quality), [splitting by flag value](usage#split-by-flag-value), and [calculating flag value frequency](usage#calculate-flag-value-frequency) are all features available also as separate scripts. This allows to perform these operations on files with previously extracted flags.
* [Filters a FASTX file with extracted flags by applying patterns to different flags](usage#match-flags-with-regular-expressions).
* Regular expression support [*fuzzy* matching](https://pypi.org/project/regex/#approximate-fuzzy-matching-hg-issue-12-hg-issue-41-hg-issue-109) (*fuzzy matching* might affect the barber's speed).
    * Optionally exports reads that do not match the provided pattern(s).
* Parallelizes processing by splitting the fastx file in chunks.

## Usage

Run:

* `fbarber` to access the barber's services.
* `fbarber flag` to extract or manipulate read flags.
* `fbarber match` to select reads based on a pattern (regular expression).
* `fbarber trim` to trim your reads.

Add `-h` to see the full help page of a command or visit the [usage page](usage)!

## Contributing

We welcome any contributions to `fastx-barber`. In short, we use [`black`](https://github.com/psf/black) to standardize code format. Any code change also needs to pass `mypy` checks. For more details, please refer to our [contribution guidelines](https://github.com/ggirelli/fastx-barber/blob/master/CONTRIBUTING.md) if this is your first time contributing! Also, check out our [code of conduct](https://github.com/ggirelli/fastx-barber/blob/master/CODE_OF_CONDUCT.md).

## License

`MIT License - Copyright (c) 2020 Gabriele Girelli`
