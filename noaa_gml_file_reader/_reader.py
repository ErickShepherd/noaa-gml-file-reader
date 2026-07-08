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

# Documented missing-value sentinels (docs/format-notes.md), mapped to NaN so
# numeric columns parse numeric instead of being dragged to object/float fill.
_NA_VALUES = ["-999.99", "-999.999", "nan"]


class UnrecognizedFormatError(Exception):
    """Raised when a file's header matches no known NOAA GML dialect.

    Carries the offending ``path`` and the file's ``first_header_line`` so the
    failure is explicit and diagnosable (replacing v1's silent empty DataFrame).
    """

    def __init__(self, path, first_header_line):
        self.path = path
        self.first_header_line = first_header_line
        super().__init__(
            f"Unrecognized NOAA GML file format: {path!r} — no "
            f"'number_of_header_lines'/'header_lines' header key found or the "
            f"header is truncated (first line: {first_header_line!r})."
        )

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
    # Current dialect: names are the last header line. A truncated file whose
    # declared header extends past EOF has no column row -> unrecognized.
    if header_count < 1 or header_count > len(lines):
        return None
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

    first_header_line = lines[0].rstrip("\n") if lines else ""

    dialect, header_count = _detect_header(lines)

    # No recognized header key: fail loudly instead of returning an empty frame.
    if dialect is None:
        raise UnrecognizedFormatError(path, first_header_line)

    names = _column_names(lines, dialect, header_count)
    if names is None:
        raise UnrecognizedFormatError(path, first_header_line)

    # One generic read for both dialects: skip the N header lines and apply the
    # per-dialect column names. engine="python" is required for the regex
    # separator under pandas >= 2; na_values maps the documented sentinels to
    # NaN so numeric columns parse numeric.
    return pd.read_csv(
        path,
        sep       = _DATA_DELIMITER,
        engine    = "python",
        names     = names,
        skiprows  = header_count,
        na_values = _NA_VALUES,
    )
