# Usage

<!-- MarkdownTOC -->

- [Match](#match)
- [Trim](#trim)
  - [Trim by length](#trim-by-length)
  - [Trim by quality](#trim-by-quality)
  - [Trim by regular expression](#trim-by-regular-expression)
- [Flags](#flags)
  - [Extract flags](#extract-flags)
    - [Flag extraction example](#flag-extraction-example)
    - [Extracting quality flags \(default\)](#extracting-quality-flags-default)
  - [After flag extraction](#after-flag-extraction)
    - [Filter by flag quality](#filter-by-flag-quality)
    - [Match flags with regular expressions](#match-flags-with-regular-expressions)
    - [Split by flag value](#split-by-flag-value)
    - [Calculate flag value frequency](#calculate-flag-value-frequency)
- [General](#general)
  - [Output](#output)
  - [Regular expressions](#regular-expressions)
  - [QSCORE](#qscore)
  - [Parallelization](#parallelization)

<!-- /MarkdownTOC -->

To access the features provided by the `fastx-barber` suite, use the `fbarber` keyword. Running `fbarber -h` provides helpful details on how to run the commands.

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

The `trim quality` allows to remove all consecutive bases with a QSCORE (`-q`) below a certain threshold, from either (`-s`) side of the reads (5': left; 3': right). For more details on the QSCORE, see [QSCORE](#qscore). This script can be parallelized; for more details see [Parallelization](#parallelization).

### Trim by regular expression

```bash
usage: fbarber trim regex [-h] [--pattern PATTERN] [--version] [--unmatched-output UNMATCHED_OUTPUT]
                          [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                          [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

The `trim regex` command tries to match a regex (`--pattern`, see [regular expressions](#regular-expression) for more details) to the reads, and then removes the portion that matched. If a read does not match the pattern, it is not written in the output; the `--unmatched-output` command can be used to export unmatched reads to a separate file instead. This script can be parallelized; for more details see [Parallelization](#parallelization).

## Flags

The `flag` command can be used to access tools to extract portions of the reads (flags) and store them in the read headers, filter them, match them to a regex, calculate statistics, or split reads besed on their value. These operations can be either performed simultaneously at time of flag extraction (see [extract flags](#extract-flags) below) or on a file with previously extracted flags (see [after flag extraction](#after-flag-extraction)).

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

By default, the part of the reads matching the pattern is trimmed, and all flags specified in the pattern are extracted (i.e., saved in the header). It is possible to extract only a subset of the flags by using the `--selected-flags` option.

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

#### Extracting quality flags (default)

When running `flag extract` on a fastq file, the portion of quality string corresponging to each flag is also stored in the header. The quality string is saved as a separate flag by appending a "q" prefix at the beginning of the flag name. To avoid extracting quality flags from fastq files, please use the `--no-qual-flags` option. The previous example applied on a fastq file,

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

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

#### Filter by flag quality

```bash
usage: fbarber flag filter [-h] [--version] [--flag-delim FLAG_DELIM] [--comment-space COMMENT_SPACE]
                           [--filter-qual-flags FILTER_QUAL_FLAGS [FILTER_QUAL_FLAGS ...]]
                           [--filter-qual-output FILTER_QUAL_OUTPUT] [--phred-offset PHRED_OFFSET]
                           [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                           [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                           in.fastx[.gz] out.fastx[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

#### Match flags with regular expressions

```bash
usage: fbarber flag regex [-h] [--pattern PATTERN [PATTERN ...]] [--version]
                          [--unmatched-output UNMATCHED_OUTPUT] [--flag-delim FLAG_DELIM]
                          [--comment-space COMMENT_SPACE] [--compress-level COMPRESS_LEVEL]
                          [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE] [--threads THREADS]
                          [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

#### Split by flag value

```bash
usage: fbarber flag split [-h] [--version] [--flag-delim FLAG_DELIM] [--comment-space COMMENT_SPACE]
                          [--split-by SPLIT_BY] [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                          [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

#### Calculate flag value frequency

```bash
usage: fbarber flag stats [-h] [--version] [--flag-delim FLAG_DELIM] [--comment-space COMMENT_SPACE]
                          [--flagstats FLAGSTATS [FLAGSTATS ...]] [--compress-level COMPRESS_LEVEL]
                          [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE] [--threads THREADS]
                          [--temp-dir TEMP_DIR]
                          in.fastx[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

## General

### Output

Lorem ipsum dolor, sit amet, consectetur adipisicing elit. Atque ipsam magni cupiditate ullam minus nemo odio ea sunt aliquam provident beatae vero earum officiis, veniam animi mollitia quia, adipisci vitae?

### Regular expressions

Lorem ipsum dolor sit amet consectetur adipisicing elit. Cupiditate, mollitia hic, dignissimos labore, facere libero officia, enim dolorum repudiandae non vel nihil. Temporibus repellendus qui, id fugit alias voluptas consequuntur.

### QSCORE

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

### Parallelization

Lorem ipsum dolor sit amet consectetur, adipisicing elit. Natus, dolore provident non molestiae nisi optio a vitae alias accusantium iste modi maxime iure magni excepturi quasi at fugiat ipsum. Possimus.
