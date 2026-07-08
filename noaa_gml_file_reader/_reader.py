"""Internal parsing implementation for noaa-gml-file-reader.

Parses NOAA GML trace-gas ASCII files into pandas DataFrames, auto-detecting the
header dialect (legacy ``# number_of_header_lines:`` vs current
``# header_lines :``). See ``docs/format-notes.md`` for the observed grammars.
"""

# Standard library imports.
import re

# Third party imports.
import pandas as pd

# The data section is whitespace-delimited (variable-width columns).
_DATA_DELIMITER = r"\s+"

# Header-length keys, one per dialect. ``\s*`` around the colon tolerates the
# observed spacing variants ("number_of_header_lines: N" vs "header_lines : N").
# The legacy key is tried first: "header_lines" is a substring of
# "number_of_header_lines", so a legacy line must not fall through to the
# current pattern.
_LEGACY_HEADER_RE  = re.compile(r"^#\s*number_of_header_lines\s*:\s*(?P<n>\d+)")
_CURRENT_HEADER_RE = re.compile(r"^#\s*header_lines\s*:\s*(?P<n>\d+)")

# The legacy dialect conveys column names via a "# data_fields:" header line.
_DATA_FIELDS_RE = re.compile(r"^#\s*data_fields\s*:\s*(?P<fields>.+)")


def _detect_header(lines):
    """Return ``(dialect, header_count)`` from the header, or ``(None, None)``.

    ``dialect`` is ``"legacy"`` or ``"current"``; ``header_count`` is the number
    of leading header lines (the data section begins on the next line).
    """
    for line in lines:
        match = _LEGACY_HEADER_RE.match(line)
        if match:
            return "legacy", int(match.group("n"))
        match = _CURRENT_HEADER_RE.match(line)
        if match:
            return "current", int(match.group("n"))
    return None, None


def _column_names(lines, dialect, header_count):
    """Extract the column names per dialect, or ``None`` if absent.

    Legacy: the ``# data_fields:`` header line. Current: the bare (non-``#``)
    column row that is the last header line (line ``header_count``, 1-indexed).
    """
    if dialect == "legacy":
        for line in lines[:header_count]:
            match = _DATA_FIELDS_RE.match(line)
            if match:
                return match.group("fields").split()
        return None
    # Current dialect: names are the last header line.
    return lines[header_count - 1].split()


def read_data(path : str) -> pd.DataFrame:

    '''

    Given the file path, this function parses an ASCII ESRL GMD data file.

    :param path: The path to the data file.
    :type path:  str

    :return:     The parsed file data.
    :rtype:      pandas.DataFrame

    '''

    with open(path) as file:
        lines = file.readlines()

    dialect, header_count = _detect_header(lines)

    # Unrecognized header dialect. (Phase 3 item 9 replaces this silent-empty
    # fallback with a raised UnrecognizedFormatError.)
    if dialect is None:
        return pd.DataFrame()

    names = _column_names(lines, dialect, header_count)
    if names is None:
        return pd.DataFrame()

    # One generic read for both dialects: skip the N header lines and apply the
    # per-dialect column names. engine="python" is required for the regex
    # separator under pandas >= 2.
    return pd.read_csv(
        path,
        sep      = _DATA_DELIMITER,
        engine   = "python",
        names    = names,
        skiprows = header_count,
    )
