"""Tests for simulate.py — simulation pipeline and CLI."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from config import PVBESSConfig
from simulate import load_and_validate_data, main, parse_args, run_simulation, save_results


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_default_config_path(self) -> None:
        with patch("sys.argv", ["simulate.py"]):
            args = parse_args()
        assert args.config == Path("data/config.yaml")
        assert args.dry_run is False
        assert args.log_level == "INFO"

    def test_custom_config(self, tmp_path: Path) -> None:
        cfg = tmp_path / "my.yaml"
        with patch("sys.argv", ["simulate.py", "--config", str(cfg)]):
            args = parse_args()
        assert args.config == cfg

    def test_dry_run_flag(self) -> None:
        with patch("sys.argv", ["simulate.py", "--dry-run"]):
            args = parse_args()
        assert args.dry_run is True

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
    def test_log_levels(self, level: str) -> None:
        with patch("sys.argv", ["simulate.py", "--log-level", level]):
            args = parse_args()
        assert args.log_level == level


# ---------------------------------------------------------------------------
# save_results
# ---------------------------------------------------------------------------

class TestSaveResults:
    def test_writes_valid_json(self, tmp_path: Path) -> None:
        results = [{"step": 0, "soc": 0.5, "bess_kw": 10.0, "grid_kw": 40.0}]
        save_results(results, tmp_path / "outputs")
        out_file = tmp_path / "outputs" / "simulation_results.json"
        assert out_file.exists()
        loaded = json.loads(out_file.read_text())
        assert loaded == results

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested" / "outputs"
        save_results([{"step": 0, "soc": 0.5, "bess_kw": 0.0, "grid_kw": 0.0}], nested)
        assert (nested / "simulation_results.json").exists()

    def test_empty_results_writes_empty_list(self, tmp_path: Path) -> None:
        save_results([], tmp_path)
        data = json.loads((tmp_path / "simulation_results.json").read_text())
        assert data == []


# ---------------------------------------------------------------------------
# run_simulation
# ---------------------------------------------------------------------------

class TestRunSimulation:
    def test_returns_correct_number_of_steps(
        self,
        minimal_config: PVBESSConfig,
        full_year_load_df: pd.DataFrame,
        full_year_pv_df: pd.DataFrame,
        full_year_weather_df: pd.DataFrame,
    ) -> None:
        results = run_simulation(
            minimal_config, full_year_load_df, full_year_pv_df, full_year_weather_df
        )
        assert len(results) == 8760

    def test_result_keys_present(
        self,
        minimal_config: PVBESSConfig,
        full_year_load_df: pd.DataFrame,
        full_year_pv_df: pd.DataFrame,
        full_year_weather_df: pd.DataFrame,
    ) -> None:
        results = run_simulation(
            minimal_config, full_year_load_df, full_year_pv_df, full_year_weather_df
        )
        assert set(results[0].keys()) == {"step", "soc", "bess_kw", "grid_kw"}

    def test_soc_stays_within_bounds(
        self,
        minimal_config: PVBESSConfig,
        full_year_load_df: pd.DataFrame,
        full_year_pv_df: pd.DataFrame,
        full_year_weather_df: pd.DataFrame,
    ) -> None:
        results = run_simulation(
            minimal_config, full_year_load_df, full_year_pv_df, full_year_weather_df
        )
        socs = [r["soc"] for r in results]
        assert all(minimal_config.bess.soc_min <= s <= minimal_config.bess.soc_max for s in socs)

    def test_bess_power_within_bounds(
        self,
        minimal_config: PVBESSConfig,
        full_year_load_df: pd.DataFrame,
        full_year_pv_df: pd.DataFrame,
        full_year_weather_df: pd.DataFrame,
    ) -> None:
        results = run_simulation(
            minimal_config, full_year_load_df, full_year_pv_df, full_year_weather_df
        )
        max_p = minimal_config.bess.power_kw
        assert all(abs(r["bess_kw"]) <= max_p + 1e-6 for r in results)

    def test_step_index_sequential(
        self,
        minimal_config: PVBESSConfig,
        full_year_load_df: pd.DataFrame,
        full_year_pv_df: pd.DataFrame,
        full_year_weather_df: pd.DataFrame,
    ) -> None:
        results = run_simulation(
            minimal_config, full_year_load_df, full_year_pv_df, full_year_weather_df
        )
        assert [r["step"] for r in results] == list(range(8760))

    @pytest.mark.slow
    def test_pv_surplus_results_in_grid_export(
        self,
        minimal_config: PVBESSConfig,
        full_year_weather_df: pd.DataFrame,
    ) -> None:
        """When PV > load the BESS charges first, then excess goes to grid (negative grid_kw)."""
        timestamps = pd.date_range("2026-01-01", periods=8760, freq="h")
        load_df = pd.DataFrame({"timestamp": timestamps, "load_kw": np.full(8760, 10.0)})
        pv_df = pd.DataFrame({"timestamp": timestamps, "pv_kw": np.full(8760, 500.0)})

        results = run_simulation(minimal_config, load_df, pv_df, full_year_weather_df)
        grid_values = [r["grid_kw"] for r in results]
        # With PV >> load the grid should be exporting (negative) in most steps
        assert any(g < 0 for g in grid_values)


# ---------------------------------------------------------------------------
# load_and_validate_data
# ---------------------------------------------------------------------------

class TestLoadAndValidateData:
    def test_returns_three_dataframes(self, minimal_config: PVBESSConfig) -> None:
        load_df, pv_df, weather_df = load_and_validate_data(minimal_config)
        assert isinstance(load_df, pd.DataFrame)
        assert isinstance(pv_df, pd.DataFrame)
        assert isinstance(weather_df, pd.DataFrame)

    def test_all_dfs_have_8760_rows(self, minimal_config: PVBESSConfig) -> None:
        load_df, pv_df, weather_df = load_and_validate_data(minimal_config)
        assert len(load_df) == 8760
        assert len(pv_df) == 8760
        assert len(weather_df) == 8760


# ---------------------------------------------------------------------------
# main (integration)
# ---------------------------------------------------------------------------

class TestMain:
    @pytest.mark.integration
    def test_dry_run_exits_zero(self, minimal_config: PVBESSConfig, tmp_path: Path) -> None:
        import yaml
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            yaml.dump({
                "simulation": {
                    "site": minimal_config.simulation.site,
                    "objective": minimal_config.simulation.objective,
                    "timestep_minutes": minimal_config.simulation.timestep_minutes,
                },
                "bess": {
                    "capacity_kwh": minimal_config.bess.capacity_kwh,
                    "power_kw": minimal_config.bess.power_kw,
                },
                "pv": {"capacity_kwp": minimal_config.pv.capacity_kwp},
                "tariff": {
                    "mode": minimal_config.tariff.mode,
                    "flat_rate_omr_per_kwh": minimal_config.tariff.flat_rate_omr_per_kwh,
                },
                "data": {
                    "loads": minimal_config.data.loads,
                    "pv_generation": minimal_config.data.pv_generation,
                    "weather": minimal_config.data.weather,
                    "outputs": minimal_config.data.outputs,
                },
            })
        )
        with patch("sys.argv", ["simulate.py", "--config", str(config_file), "--dry-run"]):
            exit_code = main()
        assert exit_code == 0

    def test_missing_config_returns_error_code(self, tmp_path: Path) -> None:
        with patch("sys.argv", [
            "simulate.py", "--config", str(tmp_path / "missing.yaml")
        ]):
            exit_code = main()
        assert exit_code == 1
