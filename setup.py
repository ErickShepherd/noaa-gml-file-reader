# Standard library imports.
import os
import sys

# Third party imports.
import setuptools

# Module dunder definitions.
#  - Versioning system: {major_version}.{minor_version}.{build_number}
__author__  = "Erick Edward Shepherd"
__version__ = "1.0.2"

setup_kwargs = {
    "name"                 : "noaa_esrl_gmd_file_reader",
    "version"              : __version__,
    "description"          : ("A package for reading NOAA ESRL GMD ASCII data"
                              "files."),
    "long_description"     : "",
    "author"               : __author__,
    "author_email"         : "dev@erickshepherd.com",
    "maintainer"           : __author__,
    "maintainer_email"     : "dev@erickshepherd.com",
    "url"                  : ("https://github.com/ErickShepherd/"
                              "noaa_esrl_gmd_file_reader"),
    "download_url"         : "",
    "packages"             : setuptools.find_packages(),
    "license"              : "AGPLv3"
}

if __name__ == "__main__":

    setuptools.setup(**setup_kwargs)
