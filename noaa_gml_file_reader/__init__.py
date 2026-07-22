"""noaa-gml-file-reader — read NOAA GML trace-gas ASCII files as DataFrames.

Public API: :func:`read_data`. The parsing implementation lives in
:mod:`noaa_gml_file_reader._reader`; the license is governed by the LICENSE file.
"""

# Local imports.
from noaa_gml_file_reader._reader import read_data, UnrecognizedFormatError

# Dunder definitions.
#  - Versioning system: {major_version}.{minor_version}.{patch}
#  - Single-sourced here; pyproject.toml reads __version__ from this module.
__author__  = "Erick Edward Shepherd"
__version__ = "2.0.4"

__all__ = ["read_data", "UnrecognizedFormatError", "__version__"]
