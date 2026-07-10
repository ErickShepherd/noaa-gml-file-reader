# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] — 2026-07-10

Citation metadata only — no code changes.

### Added
- `.zenodo.json` and an author ORCID in `CITATION.cff`, so a Zenodo release
  archive registers a citable DOI with correct software metadata.

## [2.0.1] — 2026-07-09

Docs/packaging only — no code changes.

### Changed
- Added a "Problems this solves" section to the README, mapping common
  natural-language queries (reading NOAA GML CO₂/CH₄ files, loading Mauna Loa
  flask data into pandas) to `read_data`.
- Corrected the install note — the package is published on PyPI
  (`pip install noaa-gml-file-reader`) — and narrowed the in-situ dialect table's
  empirical "seen in" column to the surveyed `(hourly)` product.
- Enriched packaging metadata: expanded keywords and added `Source` and
  `Bug Tracker` project URLs.

## [2.0.0] — 2026-07-08

Modernization release. **Breaking** — the package is renamed and unparseable
input now raises instead of returning an empty DataFrame.

### Changed
- **Renamed** the package: import `noaa_esrl_gmd_file_reader` →
  `noaa_gml_file_reader`, distribution `noaa-gml-file-reader`. NOAA renamed
  ESRL's Global Monitoring Division (GMD) to the Global Monitoring Laboratory
  (GML) in 2020.
- **`read_data` now auto-detects the header dialect** and parses both the legacy
  `# number_of_header_lines:` format and the current `# header_lines :` format,
  extracting column names correctly for each.
- Documented missing-value sentinels (`-999.99`, `-999.999`, `nan`) are mapped to
  `NaN` so numeric columns parse numeric.
- **Relicensed** AGPL-3.0 → MIT.
- Modern packaging: `pyproject.toml` (hatchling), package split into
  `_reader.py`, full type hints, and updated docstrings.

### Added
- `UnrecognizedFormatError` (carries the file path and its first line), raised on
  unrecognized, malformed, truncated, or empty input.
- Offline pytest suite over committed fixtures and a GitHub Actions CI workflow
  (ruff + pytest on Python 3.10–3.13 + `python -m build` + `twine check`).

### Removed
- The silent empty-DataFrame return on parse failure (v1 behavior) — it made a
  parse failure indistinguishable from an empty file, so v1 failed silently on
  every current NOAA file.

### Fixed
- Current (post-2020) NOAA GML files now parse instead of returning empty.
- The inconsistent GPL/AGPL wording in the v1 module docstring (removed; the
  LICENSE file governs).

## [1.0.2] — 2020-04-13

### Changed
- Linted the module: removed unused imports, added an encoding declaration, and
  removed trailing whitespace.

## [1.0.1] — 2020-03-29

### Changed
- `read_data` now returns an empty `pandas.DataFrame` (instead of `None`) when it
  fails to read a file.

## [1.0.0] — 2020-03-25

### Added
- Initial build developed and released.

[2.0.2]: https://github.com/ErickShepherd/noaa-gml-file-reader/releases/tag/v2.0.2
[2.0.1]: https://github.com/ErickShepherd/noaa-gml-file-reader/releases/tag/v2.0.1
[2.0.0]: https://github.com/ErickShepherd/noaa-gml-file-reader/releases/tag/v2.0.0
[1.0.2]: https://github.com/ErickShepherd/noaa-gml-file-reader/releases/tag/v1.0.2
[1.0.1]: https://github.com/ErickShepherd/noaa-gml-file-reader/releases/tag/v1.0.1
[1.0.0]: https://github.com/ErickShepherd/noaa-gml-file-reader/releases/tag/v1.0.0
