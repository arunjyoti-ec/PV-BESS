"""Tests for config.py — Pydantic validation of PV-BESS configuration."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from config import (
    BESSConfig,
    DataPathsConfig,
    PVBESSConfig,
    PVConfig,
    SimulationConfig,
    TariffConfig,
    load_config,
)


# ---------------------------------------------------------------------------
# BESSConfig
# ---------------------------------------------------------------------------

class TestBESSConfig:
    def test_valid_defaults(self) -> None:
        cfg = BESSConfig(capacity_kwh=500.0, power_kw=125.0)
        assert cfg.soc_min == 0.1
        assert cfg.soc_max == 0.9
        assert cfg.soc_initial == 0.5

    def test_soc_min_must_be_less_than_soc_max(self) -> None:
        with pytest.raises(ValidationError, match="soc_min"):
            BESSConfig(capacity_kwh=500.0, power_kw=125.0, soc_min=0.9, soc_max=0.1)

    def test_soc_min_equals_soc_max_raises(self) -> None:
        with pytest.raises(ValidationError, match="soc_min"):
            BESSConfig(capacity_kwh=500.0, power_kw=125.0, soc_min=0.5, soc_max=0.5)

    def test_soc_initial_below_soc_min_raises(self) -> None:
        with pytest.raises(ValidationError, match="soc_initial"):
            BESSConfig(capacity_kwh=500.0, power_kw=125.0, soc_initial=0.05, soc_min=0.1)

    def test_soc_initial_above_soc_max_raises(self) -> None:
        with pytest.raises(ValidationError, match="soc_initial"):
            BESSConfig(capacity_kwh=500.0, power_kw=125.0, soc_initial=0.95, soc_max=0.9)

    def test_capacity_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            BESSConfig(capacity_kwh=0.0, power_kw=125.0)

    def test_power_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            BESSConfig(capacity_kwh=500.0, power_kw=-10.0)

    def test_efficiency_out_of_range_raises(self) -> None:
        with pytest.raises(ValidationError):
            BESSConfig(capacity_kwh=500.0, power_kw=125.0, efficiency_charge=1.1)


# ---------------------------------------------------------------------------
# TariffConfig
# ---------------------------------------------------------------------------

class TestTariffConfig:
    def test_crt_mode_requires_tariff_file(self) -> None:
        with pytest.raises(ValidationError, match="tariff_file"):
            TariffConfig(mode="crt_2025")

    def test_tou_mode_requires_tariff_file(self) -> None:
        with pytest.raises(ValidationError, match="tariff_file"):
            TariffConfig(mode="tou")

    def test_flat_mode_requires_flat_rate(self) -> None:
        with pytest.raises(ValidationError, match="flat_rate_omr_per_kwh"):
            TariffConfig(mode="flat")

    def test_flat_mode_valid(self) -> None:
        cfg = TariffConfig(mode="flat", flat_rate_omr_per_kwh=0.025)
        assert cfg.flat_rate_omr_per_kwh == 0.025

    def test_crt_mode_with_file_valid(self) -> None:
        cfg = TariffConfig(mode="crt_2025", tariff_file="data/tariffs/oman_crt_2025.csv")
        assert cfg.tariff_file == "data/tariffs/oman_crt_2025.csv"

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(ValidationError):
            TariffConfig(mode="unknown_mode")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# SimulationConfig
# ---------------------------------------------------------------------------

class TestSimulationConfig:
    def test_valid_config(self) -> None:
        cfg = SimulationConfig(site="industrial_load", objective="cost_reduction")
        assert cfg.timestep_minutes == 60
        assert cfg.dry_run is False

    def test_timestep_must_divide_hour(self) -> None:
        with pytest.raises(ValidationError, match="divide 60"):
            SimulationConfig(
                site="industrial_load",
                objective="cost_reduction",
                timestep_minutes=7,
            )

    @pytest.mark.parametrize("minutes", [1, 5, 10, 15, 30, 60])
    def test_valid_timesteps(self, minutes: int) -> None:
        cfg = SimulationConfig(
            site="industrial_load", objective="cost_reduction", timestep_minutes=minutes
        )
        assert cfg.timestep_minutes == minutes

    def test_invalid_site_raises(self) -> None:
        with pytest.raises(ValidationError):
            SimulationConfig(site="offshore_wind", objective="cost_reduction")  # type: ignore[arg-type]

    def test_invalid_objective_raises(self) -> None:
        with pytest.raises(ValidationError):
            SimulationConfig(site="industrial_load", objective="world_domination")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# DataPathsConfig
# ---------------------------------------------------------------------------

class TestDataPathsConfig:
    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="loads"):
            DataPathsConfig(
                loads=str(tmp_path / "missing_loads.csv"),
                pv_generation=str(tmp_path / "pv.csv"),
                weather=str(tmp_path / "weather.csv"),
            )

    def test_valid_with_existing_files(self, tmp_path: Path) -> None:
        loads = tmp_path / "loads.csv"
        pv = tmp_path / "pv.csv"
        weather = tmp_path / "weather.csv"
        for f in (loads, pv, weather):
            f.write_text("timestamp,value\n2026-01-01,1.0\n")

        cfg = DataPathsConfig(loads=str(loads), pv_generation=str(pv), weather=str(weather))
        assert cfg.outputs == "data/outputs"


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig:
    def test_missing_config_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.yaml")

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("key: [unclosed bracket\n")
        with pytest.raises(Exception):
            load_config(bad_yaml)

    def test_non_mapping_yaml_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "list.yaml"
        bad_yaml.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="mapping"):
            load_config(bad_yaml)

    def test_valid_config_roundtrip(self, tmp_path: Path) -> None:
        loads = tmp_path / "loads.csv"
        pv = tmp_path / "pv.csv"
        weather = tmp_path / "weather.csv"
        for f in (loads, pv, weather):
            f.write_text("timestamp,col\n2026-01-01,1.0\n")

        config_data = {
            "simulation": {
                "site": "industrial_load",
                "objective": "cost_reduction",
                "timestep_minutes": 60,
            },
            "bess": {"capacity_kwh": 1000.0, "power_kw": 250.0},
            "pv": {"capacity_kwp": 500.0},
            "tariff": {"mode": "flat", "flat_rate_omr_per_kwh": 0.025},
            "data": {
                "loads": str(loads),
                "pv_generation": str(pv),
                "weather": str(weather),
            },
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        cfg = load_config(config_file)
        assert isinstance(cfg, PVBESSConfig)
        assert cfg.simulation.site == "industrial_load"
        assert cfg.bess.capacity_kwh == 1000.0
