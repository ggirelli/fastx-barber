# Usage

<!-- MarkdownTOC -->

- [Usage](#usage)
  - [Match](#match)
  - [Trim](#trim)
    - [Trim by length](#trim-by-length)
    - [Trim by quality](#trim-by-quality)
    - [Trim by regular expression](#trim-by-regular-expression)
  - [Flags](#flags)
    - [Extract flags](#extract-flags)
      - [Flag extraction example](#flag-extraction-example)
      - [Using a simple alphanumeric pattern](#using-a-simple-alphanumeric-pattern)
      - [Extracting quality flags (default)](#extracting-quality-flags-default)
    - [After flag extraction](#after-flag-extraction)
      - [Filter by flag quality](#filter-by-flag-quality)
      - [Match flags with regular expressions](#match-flags-with-regular-expressions)
      - [Split by flag value](#split-by-flag-value)
      - [Calculate flag value frequency](#calculate-flag-value-frequency)
  - [Find sequence](#find-sequence)
  - [General](#general)
    - [Output](#output)
    - [Regular expressions](#regular-expressions)
    - [QSCORE](#qscore)
    - [Logging](#logging)
    - [Parallelization](#parallelization)

<!-- /MarkdownTOC -->

To access the features provided by the `fastx-barber` suite, use the `fbarber` keyword.  
Running `fbarber -h` provides helpful details on how to run the commands.

## Match

```bash
usage: fbarber match [-h] [--pattern PATTERN] [--version] [--unmatched-output UNMATCHED_OUTPUT]
                     [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE]
                     [--threads THREADS] [--temp-dir TEMP_DIR]
                     in.fastx[.gz] out.fastx[.gz]
```

The `match` command allows to subselect reads from a fastx file based on a regular expression (`--pattern`, see [regular expressions](#regular-expression) for more details). Only reads matching the regex are written to the output file. It is possible to export reads that do not match the pattern through the `--unmatched-output` option. This script can be parallelized; for more details see [Parallelization](#parallelization).

## Trim

Trimming is a common operation which is generally used either to remove non-genomic (e.g., prefix, linker) read portions, or to remove terminal low-quality bases, before alignment to a reference genome. The `trim` command provides access to different tools with this aim.

### Trim by length

```bash
usage: fbarber trim length [-h] [-l LENGTH] [-s {3,5}] [--version] [--compress-level COMPRESS_LEVEL]
                           [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE] [--threads THREADS]
                           [--temp-dir TEMP_DIR]
                           in.fastx[.gz] out.fastx[.gz]
```

The `trim length` option allows to trim a given number (` -l`) of bases from either side (`-s`) of the reads (5': left; 3': right). This script can be parallelized; for more details see [Parallelization](#parallelization).

### Trim by quality

```bash
usage: fbarber trim quality [-h] [-q QSCORE] [-s {3,5}] [--version] [--phred-offset PHRED_OFFSET]
                            [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                            [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                            in.fastq[.gz] out.fastq[.gz]
```

The `trim quality` command allows to remove all consecutive bases with a QSCORE (`-q`) below a certain threshold, from either (`-s`) side of the reads (5': left; 3': right). For more details on the QSCORE, see [QSCORE](#qscore). This script can be parallelized; for more details see [Parallelization](#parallelization).

### Trim by regular expression

```bash
usage: fbarber trim regex [-h] [--pattern PATTERN] [--version] [--unmatched-output UNMATCHED_OUTPUT]
                          [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                          [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

The `trim regex` command tries to match a regex (`--pattern`, see [regular expressions](#regular-expression) for more details) to the reads, and then removes the portion that matched. If a read does not match the pattern, it is not written in the output; the `--unmatched-output` command can be used to export unmatched reads to a separate file instead. This script can be parallelized; for more details see [Parallelization](#parallelization).

## Flags

The `flag` command can be used to access tools to extract portions of the reads (flags) and store them in the read headers, filter them, match them to a regex, calculate statistics, or split reads based on their value. These operations can be either performed simultaneously at time of flag extraction (see [extract flags](#extract-flags) below) or on a file with previously extracted flags (see [after flag extraction](#after-flag-extraction)).

### Extract flags

```bash
usage: fbarber flag extract [-h] [--pattern PATTERN] [--version] [--unmatched-output UNMATCHED_OUTPUT]
                            [--flag-delim FLAG_DELIM]
                            [--selected-flags SELECTED_FLAGS [SELECTED_FLAGS ...]]
                            [--flagstats FLAGSTATS [FLAGSTATS ...]] [--split-by SPLIT_BY]
                            [--filter-qual-flags FILTER_QUAL_FLAGS [FILTER_QUAL_FLAGS ...]]
                            [--filter-qual-output FILTER_QUAL_OUTPUT] [--phred-offset PHRED_OFFSET]
                            [--no-qual-flags] [--comment-space COMMENT_SPACE]
                            [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                            [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                            in.fastx[.gz] out.fastx[.gz]
```

The `flag extract` command matches a regular expression (`--pattern`, see [regular expressions](#regular-expression) for more details) to a read. Flags can be specified in the pattern as *groups* using regular expression syntax, e.g., `^(?<umi>.{8})(?<bc>AGTCTAGA){s<2}` specifies a flag called "umi" consisting of 8 consecutive characters from the left terminal of the reads, and a second flag called "bc" with value "ACTCTAGA" allowing for up to 1 substitution (or mismatch).

By default, the part of the reads matching the pattern is trimmed, and all flags specified in the pattern are extracted (i.e., saved in the header). It is possible to extract only a subset of the flags by using the `--selected-flags` option. Moreover, use the `--unmatched-output` option to write to a separate file any read not matching the pattern.

When extracting flags, it is possible to simultaneously perform a number of operations that can also be performed <u>after</u> flag extraction:

* Use the `--flagstats` option to calculate the frequency of flag values. See [calculate flag value frequency](#calculate-flag-value-frequency) for more details.
* Use the `--filter-qual-flags` to filter reads by quality. To output reads that do <u>not</u> pass the specified filter(s), use the `--filter-qual-output` option. See [filter by flag quality](#filter-by-flag-quality) for more details.
* Split reads to different files based on the value of a flag by using the `--split-by` option. See [split by flag value](#split-by-flag-value) for more details.

This script can be parallelized; for more details see [Parallelization](#parallelization).

#### Flag extraction example

Flags are appended to the initial part of each read header, identified after removing any header comments. The `--comment-space` value (defaulting to a white space) is used to identify and remove header comments. The `--flag-delim` character (defaulting to a tilde `~`) is used to separate flags and key/value flag pairs. For example, applying the default values and the above pattern to the read below,

```
>Read_1 header_comment1 header_comment2
ACTGGACTAGTCTAGAGTATCGATCAGTCAGTCGATCG
```

would generate the following result:

```
>Read_1~~umi~ACTGGACT~~bc~AGTATAGA header_comment1 header_comment2
GTATCGATCAGTCAGTCGATCG
```

#### Using a simple alphanumeric pattern

When used together with `--simple-pattern`, the `--pattern` option accepts a *simple* alphanumeric pattern - a string composed of flag names and flag lengths. This pattern is always applied to the start (right-end, 5') of a sequence. This is especially useful to extract flags of known length, independently of their expected sequence. For example, a record starting with a UMI of 8 nt, a barcode (`BC`) of 8 nt, and a cutsite (`CS`) of 4 nt could be treated with the following pattern: `UMI8BC8CS4`. The rest of the execution proceeds in the same manner as with a normal regular expression. This can be particularly convenient as it provides a modest boost to performances.

#### Extracting quality flags (default)

When running `flag extract` on a fastq file, the portion of quality string corresponding to each flag is also stored in the header. The quality string is saved as a separate flag by appending a "q" prefix at the beginning of the flag name.

To avoid extracting quality flags from fastq files, please use the `--no-qual-flags` option.

The previous example applied on a fastq file,

```
>Read_1 header_comment1 header_comment2
ACTGGACTAGTCTAGAGTATCGATCAGTCAGTCGATCG
+
AAA/AAAAAEAAAA//AAAAAAAAAAAAAAAAAAAAAA
```

would generate the following result:

```
>Read_1~~umi~ACTGGACT~~qumi~AAA/AAAA~~bc~AGTATAGA~qbc~AEAAAA// header_comment1 header_comment2
GTATCGATCAGTCAGTCGATCG
+
AAAAAAAAAAAAAAAAAAAAAA
```

**IMPORTANT: as this approach is prone to flag name conflicts, it will change with `v0.2.0`. Follow [issue #38](https://github.com/ggirelli/fastx-barber/issues/38) for more updates. In the meantime, please refrain from using flags that start with the lettwr "q".**

### After flag extraction

As aforementioned, a number of actions can be performed either at the time of flag extraction (simultaneously), or on files with previously extracted flags. When running these commands after flag extraction, it is crucial to use the appropriate `--flag-delim` (default "~") and `--comment-space` (default " ") to properly read the flags.

#### Filter by flag quality

```bash
usage: fbarber flag filter [-h] [--version] [--flag-delim FLAG_DELIM] [--comment-space COMMENT_SPACE]
                           [--filter-qual-flags FILTER_QUAL_FLAGS [FILTER_QUAL_FLAGS ...]]
                           [--filter-qual-output FILTER_QUAL_OUTPUT] [--phred-offset PHRED_OFFSET]
                           [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                           [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                           in.fastx[.gz] out.fastx[.gz]
```

The `flag filter` command applies a set of filter(s) to one or more previously extracted flags. For each flag to be filtered, it is possible to specify a minimum QSCORE threshold and a maximum allowed fraction (percentage of bases) with QSCORE below the threshold. Specifically, the filters can be set as space-separated strings in the format `flag_name,min_QSCORE,max_fraction`.

Any read with at least a flag with more bases below the QSCORE threshold than allowed is discarded. To export reads that do <u>not</u> pass a filter, use the `--filter-qual-output` option.

For more details on the QSCORE, see [QSCORE](#qscore). This script can be parallelized; for more details see [Parallelization](#parallelization).


#### Match flags with regular expressions

```bash
usage: fbarber flag regex [-h] [--pattern PATTERN [PATTERN ...]] [--version]
                          [--unmatched-output UNMATCHED_OUTPUT] [--flag-delim FLAG_DELIM]
                          [--comment-space COMMENT_SPACE] [--compress-level COMPRESS_LEVEL]
                          [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE] [--threads THREADS]
                          [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

The `flag regex` command tries to match one or more flags to regular expressions. Any read with at least a non-matching flag, or were a specified flag is not present is not written to the output. To export these reads to a separate file, use the `--unmatched-output` option.

Regular expressions can be specified as space-separated strings in the format `"flag_name,regex"`. We recommend wrapping each string in quotes.

This script can be parallelized; for more details see [Parallelization](#parallelization).

#### Split by flag value

```bash
usage: fbarber flag split [-h] [--version] [--flag-delim FLAG_DELIM] [--comment-space COMMENT_SPACE]
                          [--split-by SPLIT_BY] [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                          [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

The `flag split` command allows to split reads to separate files based on the value of a specific flag (`--split-by`). This script can be parallelized; for more details see [Parallelization](#parallelization).

#### Calculate flag value frequency

```bash
usage: fbarber flag stats [-h] [--version] [--flag-delim FLAG_DELIM] [--comment-space COMMENT_SPACE]
                          [--flagstats FLAGSTATS [FLAGSTATS ...]] [--compress-level COMPRESS_LEVEL]
                          [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE] [--threads THREADS]
                          [--temp-dir TEMP_DIR]
                          in.fastx[.gz]
```

The `flag stats` command allows to calculate the frequency of the value of one or more flags (`--flagstats`). This script can be parallelized; for more details see [Parallelization](#parallelization).

## Find sequence

```bash
usage: fbarber find_seq [-h] [--version] [--output out.bed[.gz]] [--prefix prefix] [--case-insensitive]
                        [--global-name] [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                        in.fastx[.gz] needle
```

The `find_seq` command allows to locate a substring (`needle`) in the records of a fastx file, and produce a bed file with the extracted locations. The `--case-insensitive` option can be used to make the search case-insensitive. The generated BED file is a BED4 file where the chromosome name corresponds to the FASTX record header value, and the location name is formed by the `--prefix` value and the location ID. Location IDs are assigned incrementally per record searched. To obtain location IDs incrementing over the whole FASTX file use the `--global-name` option.

## General

### Output

For all `fbarber` commands, the format (fasta/q) of the input **must** match the output. The barber automatically detects from the output extension if the output should be compressed (expects a `.gz` suffix) using the specified compression level (`--compress-level`, defaults to 6).

### Regular expressions

`fbarber` uses the [`regex`](https://pypi.org/project/regex/) python package to compile, match, and generally manage regular expression. Thus, the barber supports *fuzzy* matching, where a number of allowed deletions/insertions/substitutions can be specified (NOTE: *fuzzy* matching might slow execution as it takes longer times to compute). Fore more details on the *fuzzy* matching syntax, please check the [`regex`](https://pypi.org/project/regex/) package documentation.

### QSCORE

`fbarber` uses the latest standard QSCORE definition of `QSCORE = -10 log10(Pe)`, were `Pe` is the error probability of a base. The QSCORE is read from the quality string of a FASTQ file using a certain PHRED offset (`--phref-offest`). The default PHRED offset is 33, following the latest Illumina standards (`chr(Q+33)`). As the barber uses the `biopython` package for quality calculation, we direct the user to [their documentation](https://biopython.org/docs/1.75/api/Bio.SeqIO.QualityIO.html), which provides a nice historical overview of the topic.

### Logging

By default, script log is written to the terminal (`stdout`). To save the output to a file we recommend using the `--log-file` option.

### Parallelization

Parallelization is achieved (using `joblib`) by splitting the input file in chunks, which are then concurrently processed on separate threads. Finally, the output of each chunk is merged into the final output by retaining the initial order.

It is possible to specify the number of reads per chunk, and the number of concurrent threadsm using the `--chunk-size` and `--threads` options, respectively. Input file chunks and single chunk output files are stored in a temporary directory, which can be changed using the `--temp-dir` option.

As the I/O operations represent the bottleneck in most operations, especially on solid-state drives and particularly when running on one read at a time, this approach can speed execution up when the chunks are large enough to be spread over multiple threads. Subprocesses are instantiated at execution start, and overhead time is proportional to the number of threads.
