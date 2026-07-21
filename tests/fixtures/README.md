# Test fixtures — NOAA GML trace-gas files

Small, committed samples used by the offline test suite (no network in tests/CI —
design §Key decisions). Each fixture is the **full header + the first ~20 data rows**
of a real file retrieved live from `https://gml.noaa.gov/aftp/data/trace_gases/`.
Header grammar and dialects are summarized in the repository
[`Supported dialects`](../../README.md#supported-dialects) section.

**Retrieval date:** 2026-07-08 · **base URL:** `https://gml.noaa.gov/aftp/data/trace_gases/`

| fixture | source path (under base URL) | dialect | trim | real/synthetic |
| --- | --- | --- | --- | --- |
| `co2_mlo_surface-flask_1_ccgg_event.txt` | `co2/flask/surface/txt/co2_mlo_surface-flask_1_ccgg_event.txt` | current (`header_lines : 149`) | `head -n 169` (149 header + 20 rows) | real |
| `ch4_mlo_surface-flask_1_ccgg_event.txt` | `ch4/flask/surface/txt/ch4_mlo_surface-flask_1_ccgg_event.txt` | current (`header_lines : 149`) | `head -n 169` (149 header + 20 rows) | real |
| `co2_mlo_surface-insitu_1_ccgg_HourlyData.txt` | `co2/in-situ/surface/txt/co2_mlo_surface-insitu_1_ccgg_HourlyData.txt` | current (`header_lines : 165`) | `head -n 185` (165 header + 20 rows) | real |
| `co2_mlo_surface-flask_1_ccgg_month.txt` | `co2/flask/surface/txt/co2_mlo_surface-flask_1_ccgg_month.txt` | legacy (`number_of_header_lines: 54`) | `head -n 74` (54 header + 20 rows) | real |
| `ch4_mlo_surface-flask_1_ccgg_month.txt` | `ch4/flask/surface/txt/ch4_mlo_surface-flask_1_ccgg_month.txt` | legacy (`number_of_header_lines: 54`) | `head -n 74` (54 header + 20 rows) | real |

## Notes

- **Both dialects are real** — the legacy `number_of_header_lines` dialect is still served
  live by the monthly product trees, so no synthetic fixture was needed.
- **Trim rule:** fixtures keep the complete header (so dialect detection and column-name
  extraction exercise the real grammar) plus the first 20 data rows. For the current dialect
  the bare column-name row is the last header line, so it is retained by the header-line trim.
- **Sentinels preserved:** the trimmed rows include real NaN sentinels (`-999.99`, `-999.999`,
  literal `nan`) where they occur in the first 20 rows, so `na_values` handling is testable.
- **All from station MLO (Mauna Loa)**; the header grammar is site- and gas-agnostic, so one
  station suffices to exercise both dialects across CO₂ and CH₄, flask (event + monthly) and
  in-situ (hourly).
- Provenance is retrieval-date-stamped; NOAA has reorganized paths before, so treat the source
  paths as historical (valid on the retrieval date), not a live contract.
