# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2]
### Fixed
- Bug in flagstats export.

## [0.1.1]
### Added
- `find_seq` option to locate needle sequence from FASTX files.
- Unit tests.
- `BedWriter` class for BED file output.
- Option for `--simple-pattern` in flag extraction.

### Changed
- Script assert errors now reported through `rich` logging.

### Fixed
- Empty output when output path is not in current working directory.
- Bug that caused log to crash script when extracting pattern matched no reads.

## [0.1.0]
### Added
- `--split-by` option to split output by flag during flag extraction.
- `flag_filter` script to apply quality filters after flag extraction.
- `trim length` to trim by length.
- `trim quality` to trim by quality.
- `flag split` to split file based on flag after flag extraction.
- `flag stats` to calculate flag stats after flag extraction.
- `flag regex` to filter flags based on regular expression after flag extraction.

### Changed
- Using rich for richer logging.
- Removed default pattern. Switched with example pattern in help page.
- Moved `trim` by pattern as command of `trim regex`.
- Moved `extract` command as sub-command of `flag`.

### Fixed
- Parallelization now working on Python 3.6+.
- Output compression now dependent only on output file extension.
- Logging proper number of reads passing flag quality filters.


## [0.0.1] - 2020-08-03

[Unreleased]: https://github.com/ggirelli/fastx-barber/tree/dev  
[0.1.2]: https://github.com/ggirelli/fastx-barber/releases/tag/v0.1.2  
[0.1.1]: https://github.com/ggirelli/fastx-barber/releases/tag/v0.1.1  
[0.1.0]: https://github.com/ggirelli/fastx-barber/releases/tag/v0.1.0  
[0.0.1]: https://github.com/ggirelli/fastx-barber/releases/tag/v0.0.1  
