# Usage

## Match

```bash
usage: fbarber match [-h] [--pattern PATTERN] [--version] [--unmatched-output UNMATCHED_OUTPUT]
                     [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE]
                     [--threads THREADS] [--temp-dir TEMP_DIR]
                     in.fastx[.gz] out.fastx[.gz]
```

Lorem ipsum dolor sit amet, consectetur adipisicing, elit. Id ab, quod repellendus, autem obcaecati illo alias, ipsam vel asperiores iure dicta voluptatem nostrum suscipit, doloremque dolores tenetur omnis recusandae repudiandae!

## Trim

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

### Trim by length

```bash
usage: fbarber trim length [-h] [-l LENGTH] [-s {3,5}] [--version] [--compress-level COMPRESS_LEVEL]
                           [--log-file LOG_FILE] [--chunk-size CHUNK_SIZE] [--threads THREADS]
                           [--temp-dir TEMP_DIR]
                           in.fastx[.gz] out.fastx[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

### Trim by quality

```bash
usage: fbarber trim quality [-h] [-q QSCORE] [-s {3,5}] [--version] [--phred-offset PHRED_OFFSET]
                            [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                            [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                            in.fastq[.gz] out.fastq[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

### Trim by regular expression

```bash
usage: fbarber trim regex [-h] [--pattern PATTERN] [--version] [--unmatched-output UNMATCHED_OUTPUT]
                          [--compress-level COMPRESS_LEVEL] [--log-file LOG_FILE]
                          [--chunk-size CHUNK_SIZE] [--threads THREADS] [--temp-dir TEMP_DIR]
                          in.fastx[.gz] out.fastx[.gz]
```

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

## Flags

Lorem ipsum dolor sit amet, consectetur, adipisicing elit. Voluptate consectetur adipisci maxime ducimus voluptatem vero illo recusandae accusamus dolores rerum nemo similique vel amet, quidem possimus eligendi veniam quae officia.

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

Lorem ipsum dolor sit, amet consectetur, adipisicing elit. Veritatis eaque modi ipsam sit laudantium consequatur accusamus voluptatibus aut suscipit! Autem iste minima laborum, quam magni doloribus consequatur eligendi asperiores sed!

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