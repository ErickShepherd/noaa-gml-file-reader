# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import re
import sys

# Make the package importable for autodoc without installing it.
_repo_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo_root))

# -- Project information ------------------------------------------------------

project   = "noaa-gml-file-reader"
author    = "Erick Edward Shepherd"
copyright = "2020-2026, Erick Edward Shepherd"

# Single-source the version from the package without importing it (pandas is
# not installed in the docs build).
_init   = (_repo_root / "noaa_gml_file_reader" / "__init__.py").read_text(encoding="utf-8")
release = re.search(r'__version__\s*=\s*"([^"]+)"', _init).group(1)
version = release

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

# pandas is mocked so the docs build needs no scientific stack; autodoc only
# imports the package to read its docstrings.
autodoc_mock_imports = ["pandas"]

autodoc_member_order = "bysource"
autodoc_typehints    = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path   = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "design",
    "plans",
    "release-checklist.md",
    # Internal parser-evidence survey tied to the (excluded) plan documents;
    # the README and docstrings carry the user-facing dialect summary.
    "format-notes.md",
]

# -- HTML output --------------------------------------------------------------

html_theme = "furo"
html_title = f"noaa-gml-file-reader {release}"
html_theme_options = {
    # Backlink to the author's site in the page footer.
    "footer_icons": [
        {
            "name": "erickshepherd.com",
            "url": "https://erickshepherd.com",
            "html": "erickshepherd.com",
            "class": "",
        },
    ],
}
