# noaa-gml-file-reader

[![CI](https://github.com/ErickShepherd/noaa-gml-file-reader/actions/workflows/ci.yml/badge.svg)](https://github.com/ErickShepherd/noaa-gml-file-reader/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Read [NOAA GML](https://gml.noaa.gov) atmospheric trace-gas ASCII data files as
[`pandas.DataFrame`](https://pandas.pydata.org/) objects — one function,
`read_data(path)`.

## What this reads

NOAA's Global Monitoring Laboratory (GML) publishes long-term atmospheric
trace-gas measurements (CO₂, CH₄, and others) as whitespace-delimited ASCII
files with a `#`-commented header — surface-flask **event** and **monthly**
series, in-situ **hourly**/daily series, and more, at
[gml.noaa.gov/aftp/data/trace_gases](https://gml.noaa.gov/aftp/data/trace_gases/).
This package turns one of those files into a tidy DataFrame, with the header's
column names and the documented missing-value sentinels handled for you.

> **Lineage (GMD → GML).** NOAA renamed ESRL's Global Monitoring *Division*
> (GMD) to the Global Monitoring *Laboratory* (GML) in 2020, and the file header
> format changed with it. This package was originally `noaa_esrl_gmd_file_reader`
> (2020); v2 renames it to **noaa-gml-file-reader** (import `noaa_gml_file_reader`)
> and reads the current header format. See the breaking-change note below.

## Install

```bash
pip install noaa-gml-file-reader
```

Requires Python ≥ 3.10 and pandas ≥ 2.0. (Not yet on PyPI — install from source:
`pip install git+https://github.com/ErickShepherd/noaa-gml-file-reader`.)

## Usage

```python
from noaa_gml_file_reader import read_data

df = read_data("co2_mlo_surface-flask_1_ccgg_month.txt")
print(df.head())
```

Real output (from the committed test fixture of the above Mauna Loa monthly file):

```
  site  year  month   value
0  MLO  1969      8  322.50
1  MLO  1969      9  321.36
2  MLO  1969     10  320.74
3  MLO  1969     11  321.98
4  MLO  1969     12  323.78
```

Columns come straight from the file's header; numeric columns are numeric
(`value` is `float64`, `year`/`month` are `int64`), and NOAA's missing-value
sentinels (`-999.99`, `-999.999`, `nan`) are parsed as `NaN`.

## Supported dialects

`read_data` auto-detects the header dialect — you don't need to know NOAA's
format history to read a file:

| dialect | header key | column names from | seen in |
| --- | --- | --- | --- |
| **current** | `# header_lines : N` | the bare column row that is the last header line | flask **event**, **in-situ** (hourly/daily) |
| **legacy** (2020) | `# number_of_header_lines: N` | the `# data_fields:` header line | flask **monthly** |

Supported products are those catalogued in [`docs/format-notes.md`](docs/format-notes.md)
(CO₂/CH₄ surface-flask event + monthly, CO₂ in-situ hourly, at MLO). The header
grammar is site- and gas-agnostic, so other stations/species in the same product
families parse the same way.

## Errors

An unparseable file **raises** `UnrecognizedFormatError` (carrying the path and
the file's first line) rather than returning data:

```python
from noaa_gml_file_reader import read_data, UnrecognizedFormatError

try:
    df = read_data("not-a-noaa-file.txt")
except UnrecognizedFormatError as err:
    print(err)
```

## v2 breaking changes

v2 is a breaking release (hence the major bump):

- **Renamed** `noaa_esrl_gmd_file_reader` → `noaa_gml_file_reader`
  (distribution `noaa-gml-file-reader`).
- **Raises `UnrecognizedFormatError`** on unrecognized/malformed input. v1
  returned an *empty DataFrame* on any parse failure — silently indistinguishable
  from "the file had no data" — which meant v1 failed silently on every current
  (post-2020) NOAA file. If you relied on the empty-DataFrame behavior, catch the
  exception instead.
- **Relicensed** AGPL-3.0 → MIT.

## Data & citation

The data are NOAA GML's, not this package's. Please cite the measurements per
NOAA GML's guidance — each product directory under
[gml.noaa.gov/aftp/data/trace_gases](https://gml.noaa.gov/aftp/data/trace_gases/)
ships a species-specific README with the citation text and data providers (the
file headers also carry contact and reciprocity information). This library only
parses the files; it does not download them.

## License

MIT — see [LICENSE](LICENSE).
