"""Tests for validators.py — CSV loading and physical sanity checks."""
from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from validators import (
    check_energy_balance,
    check_power_bounds,
    check_soc,
    load_csv,
    validate_load_profile,
    validate_pv_generation,
    validate_weather,
)


# ---------------------------------------------------------------------------
# load_csv
# ---------------------------------------------------------------------------

class TestLoadCSV:
    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="load profile"):
            load_csv(tmp_path / "missing.csv", label="load profile")

    def test_empty_file_raises_value_error(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.csv"
        empty.write_text("timestamp,load_kw\n")
        with pytest.raises(ValueError, match="empty"):
            load_csv(empty, label="load profile")

    def test_valid_csv_returns_dataframe(self, tmp_path: Path) -> None:
        f = tmp_path / "loads.csv"
        f.write_text("timestamp,load_kw\n2026-01-01 00:00:00,100.0\n")
        df = load_csv(f, label="load profile")
        assert len(df) == 1
        assert "load_kw" in df.columns

    def test_timestamp_parsed_as_datetime(self, tmp_path: Path) -> None:
        f = tmp_path / "loads.csv"
        f.write_text("timestamp,load_kw\n2026-01-01 00:00:00,100.0\n")
        df = load_csv(f, label="load profile")
        assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])

    def test_missing_timestamp_column_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.csv"
        f.write_text("date,load_kw\n2026-01-01,100.0\n")
        with pytest.raises(ValueError):
            load_csv(f, label="load profile")


# ---------------------------------------------------------------------------
# validate_load_profile
# ---------------------------------------------------------------------------

class TestValidateLoadProfile:
    def test_valid_df_passes(self, sample_load_df: pd.DataFrame) -> None:
        result = validate_load_profile(sample_load_df)
        assert "load_kw" in result.columns

    def test_missing_column_raises(self) -> None:
        bad = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=3, freq="h")})
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_load_profile(bad)

    def test_nan_in_load_kw_raises(self, sample_load_df: pd.DataFrame) -> None:
        sample_load_df.loc[0, "load_kw"] = float("nan")
        with pytest.raises(ValueError, match="NaN"):
            validate_load_profile(sample_load_df)

    def test_negative_load_raises(self, sample_load_df: pd.DataFrame) -> None:
        sample_load_df.loc[0, "load_kw"] = -10.0
        with pytest.raises(ValueError, match="negative"):
            validate_load_profile(sample_load_df)

    def test_unsorted_timestamps_raises(self, sample_load_df: pd.DataFrame) -> None:
        shuffled = sample_load_df.iloc[::-1].reset_index(drop=True)
        with pytest.raises(ValueError, match="sorted"):
            validate_load_profile(shuffled)

    def test_duplicate_timestamps_raises(self, sample_load_df: pd.DataFrame) -> None:
        duped = pd.concat([sample_load_df, sample_load_df.iloc[[0]]], ignore_index=True)
        duped = duped.sort_values("timestamp").reset_index(drop=True)
        with pytest.raises(ValueError, match="duplicate"):
            validate_load_profile(duped)


# ---------------------------------------------------------------------------
# validate_pv_generation
# ---------------------------------------------------------------------------

class TestValidatePVGeneration:
    def test_valid_df_passes(self, sample_pv_df: pd.DataFrame) -> None:
        result = validate_pv_generation(sample_pv_df)
        assert "pv_kw" in result.columns

    def test_negative_pv_raises(self, sample_pv_df: pd.DataFrame) -> None:
        sample_pv_df.loc[0, "pv_kw"] = -5.0
        with pytest.raises(ValueError, match="negative"):
            validate_pv_generation(sample_pv_df)

    def test_nan_in_pv_raises(self, sample_pv_df: pd.DataFrame) -> None:
        sample_pv_df.loc[0, "pv_kw"] = float("nan")
        with pytest.raises(ValueError, match="NaN"):
            validate_pv_generation(sample_pv_df)


# ---------------------------------------------------------------------------
# validate_weather
# ---------------------------------------------------------------------------

class TestValidateWeather:
    def test_valid_df_passes(self, sample_weather_df: pd.DataFrame) -> None:
        result = validate_weather(sample_weather_df)
        assert "irradiance_wm2" in result.columns
        assert "temperature_c" in result.columns

    def test_nan_in_irradiance_raises(self, sample_weather_df: pd.DataFrame) -> None:
        sample_weather_df.loc[0, "irradiance_wm2"] = float("nan")
        with pytest.raises(ValueError, match="NaN"):
            validate_weather(sample_weather_df)

    def test_negative_irradiance_raises(self, sample_weather_df: pd.DataFrame) -> None:
        sample_weather_df.loc[0, "irradiance_wm2"] = -1.0
        with pytest.raises(ValueError, match="negative"):
            validate_weather(sample_weather_df)

    def test_out_of_range_irradiance_warns(
        self, sample_weather_df: pd.DataFrame, caplog: pytest.LogCaptureFixture
    ) -> None:
        sample_weather_df.loc[0, "irradiance_wm2"] = 2000.0
        with caplog.at_level("WARNING"):
            validate_weather(sample_weather_df)
        assert any("outside" in r.message for r in caplog.records)

    def test_out_of_range_temperature_warns(
        self, sample_weather_df: pd.DataFrame, caplog: pytest.LogCaptureFixture
    ) -> None:
        sample_weather_df.loc[0, "temperature_c"] = 70.0
        with caplog.at_level("WARNING"):
            validate_weather(sample_weather_df)
        assert any("outside" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# check_soc
# ---------------------------------------------------------------------------

class TestCheckSOC:
    def test_valid_soc_passes(self) -> None:
        check_soc(0.5, soc_min=0.1, soc_max=0.9)

    def test_soc_at_min_boundary_passes(self) -> None:
        check_soc(0.1, soc_min=0.1, soc_max=0.9)

    def test_soc_at_max_boundary_passes(self) -> None:
        check_soc(0.9, soc_min=0.1, soc_max=0.9)

    def test_soc_below_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="physical bounds"):
            check_soc(-0.01, soc_min=0.1, soc_max=0.9, step=5)

    def test_soc_above_one_raises(self) -> None:
        with pytest.raises(ValueError, match="physical bounds"):
            check_soc(1.01, soc_min=0.1, soc_max=0.9)

    def test_soc_below_min_raises(self) -> None:
        with pytest.raises(ValueError, match="soc_min"):
            check_soc(0.05, soc_min=0.1, soc_max=0.9, step=10)

    def test_soc_above_max_raises(self) -> None:
        with pytest.raises(ValueError, match="soc_max"):
            check_soc(0.95, soc_min=0.1, soc_max=0.9)

    def test_step_appears_in_error_message(self) -> None:
        with pytest.raises(ValueError, match="timestep 42"):
            check_soc(-0.1, soc_min=0.1, soc_max=0.9, step=42)


# ---------------------------------------------------------------------------
# check_power_bounds
# ---------------------------------------------------------------------------

class TestCheckPowerBounds:
    def test_valid_charge_passes(self) -> None:
        check_power_bounds(-250.0, max_power_kw=250.0)

    def test_valid_discharge_passes(self) -> None:
        check_power_bounds(250.0, max_power_kw=250.0)

    def test_zero_passes(self) -> None:
        check_power_bounds(0.0, max_power_kw=250.0)

    def test_exceeding_raises(self) -> None:
        with pytest.raises(ValueError, match="exceeds rated"):
            check_power_bounds(300.0, max_power_kw=250.0, step=1)

    def test_exceeding_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="exceeds rated"):
            check_power_bounds(-300.0, max_power_kw=250.0)

    def test_tolerance_allows_tiny_overshoot(self) -> None:
        # Should NOT raise for floating point rounding artefacts
        check_power_bounds(250.000001, max_power_kw=250.0)


# ---------------------------------------------------------------------------
# check_energy_balance
# ---------------------------------------------------------------------------

class TestCheckEnergyBalance:
    def test_balanced_system_passes(self) -> None:
        # load = pv + bess_discharge + grid_import
        check_energy_balance(
            load_kw=150.0, pv_kw=100.0, bess_kw=30.0, grid_kw=20.0,
            timestep_h=1.0,
        )

    def test_imbalance_raises(self) -> None:
        with pytest.raises(ValueError, match="imbalance"):
            check_energy_balance(
                load_kw=150.0, pv_kw=100.0, bess_kw=30.0, grid_kw=5.0,
                timestep_h=1.0,
            )

    def test_step_in_error_message(self) -> None:
        with pytest.raises(ValueError, match="timestep 99"):
            check_energy_balance(
                load_kw=100.0, pv_kw=0.0, bess_kw=0.0, grid_kw=200.0,
                timestep_h=1.0, step=99,
            )

    def test_custom_tolerance(self) -> None:
        # Imbalance of 0.5 kW — within 1.0 kW tolerance
        check_energy_balance(
            load_kw=100.5, pv_kw=100.0, bess_kw=0.0, grid_kw=0.0,
            timestep_h=1.0, tolerance_kw=1.0,
        )

    def test_export_scenario_passes(self) -> None:
        # PV surplus exported: grid_kw < 0
        check_energy_balance(
            load_kw=50.0, pv_kw=100.0, bess_kw=0.0, grid_kw=-50.0,
            timestep_h=1.0,
        )
