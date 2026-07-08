"""Internal parsing implementation for noaa-gml-file-reader.

This module holds the parsing logic; the public API is re-exported from the
package's ``__init__``. (Phase 2 move only — the parser body is unchanged from
v1 here; the v2 dialect-aware rewrite lands in Phase 3.)
"""

# Standard library imports.
import re

# Third party imports.
import pandas as pd

# Constant definitions.
_DATA_DELIMITER_REGEX = r"\s+"
_HEADER_LINES_REGEX   = r"# number_of_header_lines: (?P<header_lines>\d+)"
_DATA_FIELDS_REGEX    = r"# data_fields: (?P<data_fields>.+)"


def read_data(path : str) -> pd.DataFrame:

    '''

    Given the file path, this function parses an ASCII ESRL GMD data file.

    :param path: The path to the data file.
    :type path:  str

    :return:     The parsed file data.
    :rtype:      pandas.DataFrame

    '''

    # Opens the file.
    with open(path) as file:

        # Defines variables to store the values extracted from the regular
        # expression groups.
        header_lines, data_fields = None, None

        # Iterates through the file.
        for line in file:

            # Checks whether the line matches the header lines regular
            # expression provided that a match has not already occurred.
            if not header_lines:

                header_lines_match = re.match(_HEADER_LINES_REGEX, line)

                # If the regular expression yields a match, extract the number
                # of header lines from the string.
                if header_lines_match:

                    header_lines = header_lines_match.groupdict()
                    header_lines = header_lines["header_lines"]

            # Checks whether the line matches the data fields regular
            # expression provided that a match has not already occurred.
            if not data_fields:

                data_fields_match = re.match(_DATA_FIELDS_REGEX, line)

                # If the regular expression yields a match, extract the data
                # fields from the string.
                if data_fields_match:

                    data_fields = data_fields_match.groupdict()
                    data_fields = data_fields["data_fields"]

            if bool(header_lines and data_fields):

                break

    # Checks whether the regular expressions were matched. If so, this reads
    # the file as a CSV and returns a pandas.DataFrame. Otherwise, it returns
    # an empty DataFrame.
    if bool(header_lines and data_fields):

        # Casts the header lines as an integer and splits the data fields
        # into a list.
        header_lines = int(header_lines)
        data_fields  = re.split(_DATA_DELIMITER_REGEX, data_fields)

        # Reads the file as a CSV with a regular expression delimiter and the
        # data fields as the column names after skipping the given number of
        # header lines.
        data = pd.read_csv(path,
                           delimiter = _DATA_DELIMITER_REGEX,
                           names     = data_fields,
                           skiprows  = header_lines)

        return data

    else:

        return pd.DataFrame()
