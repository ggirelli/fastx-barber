# fastx-barber

[![DOI](https://zenodo.org/badge/281703558.svg)](https://zenodo.org/badge/latestdoi/281703558) ![](https://img.shields.io/librariesio/github/ggirelli/fastx-barber.svg?style=flat) ![](https://img.shields.io/github/license/ggirelli/fastx-barber.svg?style=flat)  
![](https://github.com/ggirelli/fastx-barber/workflows/Python%20package/badge.svg?branch=main&event=push) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastx-barber) ![PyPI - Format](https://img.shields.io/pypi/format/fastx-barber) ![PyPI - Status](https://img.shields.io/pypi/status/fastx-barber)  
![](https://img.shields.io/github/release/ggirelli/fastx-barber.svg?style=flat) ![](https://img.shields.io/github/release-date/ggirelli/fastx-barber.svg?style=flat) ![](https://img.shields.io/github/languages/code-size/ggirelli/fastx-barber.svg?style=flat)  
![](https://img.shields.io/github/watchers/ggirelli/fastx-barber.svg?label=Watch&style=social) ![](https://img.shields.io/github/stars/ggirelli/fastx-barber.svg?style=social)

[PyPi](https://pypi.org/project/fastx-barber/) | [docs](https://ggirelli.github.io/fastx-barber/)

A Python3.6.13+ package to trim and extract flags from FASTA  and FASTQ files.

## Features (in short)

* Works on both FASTA and FASTQ files.
* Selects reads based on a pattern (regex).
* Trims reads by pattern (regex), length, or single-base quality.
* Extracts parts (flags) of reads based on a pattern and stores them in the read headers.
* [Generates BED file with the locations of a substring](usage#find-sequence) in FASTX records.
* Regular expression support [*fuzzy* matching](https://pypi.org/project/regex/#approximate-fuzzy-matching-hg-issue-12-hg-issue-41-hg-issue-109) (*fuzzy matching* might affect the barber's speed).
* Parallelizes processing by splitting the fastx file in chunks.

For more available features, check out our [docs](https://ggirelli.github.io/fastx-barber/)!

## Requirements

`fastx-barber` has been tested with Python 3.6.13, 3.7, 3.8, and 3.9. We recommend installing it using `pipx` (see [below](https://github.com/ggirelli/fastx-barber#install)) to avoid dependency conflicts with other packages. The packages it depends on are listed in our [dependency graph](https://github.com/ggirelli/fastx-barber/network/dependencies). We use [`poetry`](https://github.com/python-poetry/poetry) to handle our dependencies.

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

We welcome any contributions to `fastx-barber`. In short, we use [`black`](https://github.com/psf/black) to standardize code format. Any code change also needs to pass `mypy` checks. For more details, please refer to our [contribution guidelines](https://github.com/ggirelli/fastx-barber/blob/main/CONTRIBUTING.md) if this is your first time contributing! Also, check out our [code of conduct](https://github.com/ggirelli/fastx-barber/blob/main/CODE_OF_CONDUCT.md).

## License

`MIT License - Copyright (c) 2020 Gabriele Girelli`
