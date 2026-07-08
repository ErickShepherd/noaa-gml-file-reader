#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

A package for reading NOAA ESRL GMD ASCII data files.

Author:         Erick Edward Shepherd
E-mail:         dev@erickshepherd.com
GitHub:         github.com/ErickShepherd
Version:        1.0.2
Date created:   2020-03-25
Last modified:  2020-03-29


Description:
    
    A Python 3 module for reading Search NOAA Earth System Research Laboratory
    (ESRL) Global Monitoring Division (GMD) ASCII data files and parsing them
    as pandas.DataFrame objects.


Copyright:

    Copyright (C) 2020 of Erick Edward Shepherd, all rights reserved.


License:
    
    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation, either version 3 of the License, or (at your
    option) any later version.

    This program is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
    more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
    
    
Changelog:
    
    2020-03-25 - Version 1.0.0:
        
        Initial build developed and released.
        
    2020-03-29 - Version 1.0.1:
    
        Changed the return type of the "read_data" function in the event of a
        failed attempt to read the file from a None object to an empty
        pandas.DataFrame.
        
    2020-04-13 - Version 1.0.2:
        
        Linted the module: removed unused imports, added an encoding
        declaration, and removed trailing whitespace.

'''

# Standard library imports.
import re

# Third party imports.
import pandas as pd

# Dunder definitions.
#  - Versioning system: {major_version}.{minor_version}.{patch}
__author__  = "Erick Edward Shepherd"
__version__ = "1.0.2"

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
    # the file as a CVS and returns a pandas.DataFrame. Otherwise, it returns
    # a None object.
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
