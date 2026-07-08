"""Offline tests for noaa_gml_file_reader.read_data over the committed fixtures.

Covers both header dialects (shape / columns / dtypes / spot values), the NaN
sentinel mapping, and that malformed / truncated / empty inputs raise
UnrecognizedFormatError. No network access.
"""

from pathlib import Path

import pandas as pd
import pytest

from noaa_gml_file_reader import read_data, UnrecognizedFormatError

FIXTURES = Path(__file__).parent / "fixtures"

LEGACY_MONTHLY = [
    "co2_mlo_surface-flask_1_ccgg_month.txt",
    "ch4_mlo_surface-flask_1_ccgg_month.txt",
]
CURRENT_EVENT = [
    "co2_mlo_surface-flask_1_ccgg_event.txt",
    "ch4_mlo_surface-flask_1_ccgg_event.txt",
]
INSITU_HOURLY = "co2_mlo_surface-insitu_1_ccgg_HourlyData.txt"


def _read(name: str) -> pd.DataFrame:
    return read_data(str(FIXTURES / name))


# --------------------------------------------------------------------------- #
# Per-dialect shape / columns / dtypes
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", LEGACY_MONTHLY)
def test_legacy_dialect_shape_columns_dtypes(name):
    df = _read(name)
    assert list(df.columns) == ["site", "year", "month", "value"]
    assert len(df) == 20
    assert pd.api.types.is_numeric_dtype(df["value"])
    assert pd.api.types.is_numeric_dtype(df["year"])


@pytest.mark.parametrize("name", CURRENT_EVENT)
def test_current_event_shape_columns_dtypes(name):
    df = _read(name)
    assert len(df) == 20
    assert len(df.columns) == 22
    assert list(df.columns[:4]) == ["site_code", "year", "month", "day"]
    for col in ("value", "value_unc", "latitude", "qcflag"):
        assert col in df.columns
    assert pd.api.types.is_numeric_dtype(df["value"])
    # qcflag is a 3-character string flag, must NOT be coerced to numeric
    # (pandas >= 3 uses StringDtype, < 3 uses object — assert "not numeric").
    assert not pd.api.types.is_numeric_dtype(df["qcflag"])


def test_current_insitu_hourly_shape():
    df = _read(INSITU_HOURLY)
    assert len(df) == 20
    assert len(df.columns) == 21
    assert list(df.columns[:4]) == ["site_code", "year", "month", "day"]
    assert pd.api.types.is_numeric_dtype(df["value"])


# --------------------------------------------------------------------------- #
# Spot values (fixtures are frozen, so these are stable)
# --------------------------------------------------------------------------- #

def test_spot_values_legacy_co2_month():
    df = _read("co2_mlo_surface-flask_1_ccgg_month.txt")
    row = df.iloc[0]
    assert row["site"] == "MLO"
    assert int(row["year"]) == 1969
    assert int(row["month"]) == 8
    assert row["value"] == pytest.approx(322.50)


def test_spot_values_current_co2_event():
    df = _read("co2_mlo_surface-flask_1_ccgg_event.txt")
    row = df.iloc[0]
    assert row["site_code"] == "MLO"
    assert int(row["year"]) == 1969
    assert row["value"] == pytest.approx(323.17)


# --------------------------------------------------------------------------- #
# NaN sentinel handling
# --------------------------------------------------------------------------- #

def test_sentinels_mapped_to_nan_insitu():
    df = _read(INSITU_HOURLY)
    # every one of the first 20 in-situ value rows is a -999.99 sentinel
    assert df["value"].isna().all()
    # the literal sentinel must not survive as a real numeric value
    assert not (df["value"] == -999.99).any()


def test_sentinels_mapped_to_nan_event():
    df = _read("co2_mlo_surface-flask_1_ccgg_event.txt")
    assert df["value"].isna().any()          # this fixture has sentinel rows
    assert not (df["value"] == -999.99).any()
    assert not (df["value_unc"] == -999.999).any()


# --------------------------------------------------------------------------- #
# Malformed / truncated / empty inputs raise
# --------------------------------------------------------------------------- #

def test_empty_file_raises(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("")
    with pytest.raises(UnrecognizedFormatError):
        read_data(str(p))


def test_garbage_no_header_key_raises(tmp_path):
    p = tmp_path / "garbage.txt"
    p.write_text("not a NOAA file\njust text\n")
    with pytest.raises(UnrecognizedFormatError):
        read_data(str(p))


def test_truncated_current_header_raises(tmp_path):
    # declares 149 header lines but the file is only 3 lines long
    p = tmp_path / "truncated.txt"
    p.write_text("# header_lines : 149\n# comment\nMLO 2020 1\n")
    with pytest.raises(UnrecognizedFormatError):
        read_data(str(p))


def test_legacy_without_data_fields_raises(tmp_path):
    p = tmp_path / "nofields.txt"
    p.write_text("# number_of_header_lines: 3\n# comment\n# comment\nMLO 1 2 3\n")
    with pytest.raises(UnrecognizedFormatError):
        read_data(str(p))


def test_exception_carries_path_and_first_line(tmp_path):
    p = tmp_path / "bad.txt"
    p.write_text("garbage first line\nsecond line\n")
    with pytest.raises(UnrecognizedFormatError) as excinfo:
        read_data(str(p))
    assert excinfo.value.path == str(p)
    assert excinfo.value.first_header_line == "garbage first line"
