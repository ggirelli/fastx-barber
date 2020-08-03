# fastx-barber

A Python3.6+ package to trim and extract flags from FASTA  and FASTQ files.

## Features

* Supports both FASTA and FASTQ files.
* Select your reads based on a pattern (regular expression).
* Trim your reads based on a pattern (regular expression).
* Extract parts (flags) of reads based on a pattern and store them in the read headers.
    - Extract the corresponding portions of the quality string too (only for fastq files).
* All patterns use the `regex` Python package to support [*fuzzy* matching](https://pypi.org/project/regex/#approximate-fuzzy-matching-hg-issue-12-hg-issue-41-hg-issue-109).
    - Using fuzzy matching might affect the barber's speed).
* Export reads that do not match the provided pattern.
* Parallelized processing by splitting the fastx file in chunks.
* Filter reads based on quality score of extracted flags.
    - Supports Sanger QSCORE definition (not old Solexa/Illumina one), and allows to specify different PHRED offsets.

## Requirements

`fastx-barber` has been tested with Python 3.6, 3.7, and 3.8. We recommend installing it using `pipx` (see [below](https://github.com/ggirelli/fastx-barber#install)) to avoid dependency conflicts with other packages. The packages it depends on are listed in our [dependency graph](https://github.com/ggirelli/fastx-barber/network/dependencies). We use [`poetry`](https://github.com/python-poetry/poetry) to handle our dependencies.

## Install

We recommend installing `fastx-barber` using [`pipx`](https://github.com/pipxproject/pipx). Check how to install `pipx` [here](https://github.com/pipxproject/pipx#install-pipx) if you don't have it yet!

Once you have `pipx` ready on your system, install the latest stable release of `fastx-barber` by running: `pipx install fastx-barber`. If you see the stars (✨ 🌟 ✨), then the installation went well!

## Usage

Run:

* `fbarber` to access the barber's services.
* `fbarber trim` to trim your reads.
* `fbarber match` to select reads based on a pattern (regular expression).
* `fbarber extract` to extract parts of a read and store them in the read name, and then trim it.

Add `-h` to see the full help page of a command!

## Contributing

We welcome any contributions to `fastx-barber`. In short, we use [`black`](https://github.com/psf/black) to standardize code format. Any code change also needs to pass `mypy` checks. For more details, please refer to our [contribution guidelines](https://github.com/ggirelli/fastx-barber/blob/master/CONTRIBUTING.md) if this is your first time contributing! Also, check out our [code of conduct](https://github.com/ggirelli/fastx-barber/blob/master/CODE_OF_CONDUCT.md).

## License

`MIT License - Copyright (c) 2020 Gabriele Girelli`
