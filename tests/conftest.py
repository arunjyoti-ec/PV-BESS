"""Shared pytest fixtures for PV-BESS tests."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is importable from tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    BESSConfig,
    DataPathsConfig,
    PVBESSConfig,
    PVConfig,
    SimulationConfig,
    TariffConfig,
)


# ---------------------------------------------------------------------------
# Minimal DataFrame fixtures (24-hour slices — fast for unit tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_load_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "timestamp": timestamps,
        "load_kw": (rng.random(24) * 100 + 50).astype("float64"),
    })


@pytest.fixture
def sample_pv_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    pv = np.zeros(24)
    pv[6:18] = np.linspace(0, 200, 12)  # daytime ramp
    return pd.DataFrame({"timestamp": timestamps, "pv_kw": pv.astype("float64")})


@pytest.fixture
def sample_weather_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    irr = np.zeros(24)
    irr[6:18] = np.linspace(0, 800, 12)
    return pd.DataFrame({
        "timestamp": timestamps,
        "irradiance_wm2": irr.astype("float64"),
        "temperature_c": np.full(24, 35.0),
    })


# ---------------------------------------------------------------------------
# Full-year DataFrame fixtures (8760 rows — used for integration tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def full_year_load_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=8760, freq="h")
    return pd.DataFrame({
        "timestamp": timestamps,
        "load_kw": np.full(8760, 100.0),
    })


@pytest.fixture
def full_year_pv_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=8760, freq="h")
    return pd.DataFrame({
        "timestamp": timestamps,
        "pv_kw": np.full(8760, 50.0),
    })


@pytest.fixture
def full_year_weather_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=8760, freq="h")
    return pd.DataFrame({
        "timestamp": timestamps,
        "irradiance_wm2": np.full(8760, 500.0),
        "temperature_c": np.full(8760, 30.0),
    })


# ---------------------------------------------------------------------------
# Config sub-model fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_bess_config() -> BESSConfig:
    return BESSConfig(capacity_kwh=1000.0, power_kw=250.0)


@pytest.fixture
def valid_pv_config() -> PVConfig:
    return PVConfig(capacity_kwp=500.0)


@pytest.fixture
def valid_simulation_config() -> SimulationConfig:
    return SimulationConfig(site="industrial_load", objective="cost_reduction")


@pytest.fixture
def flat_tariff_config() -> TariffConfig:
    return TariffConfig(mode="flat", flat_rate_omr_per_kwh=0.025)


# ---------------------------------------------------------------------------
# Full PVBESSConfig fixture backed by real tmp CSV files
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_config(tmp_path: Path) -> PVBESSConfig:
    """A complete PVBESSConfig using temp files — safe for file-existence checks."""
    timestamps = pd.date_range("2026-01-01", periods=8760, freq="h")

    loads_path = tmp_path / "loads.csv"
    pd.DataFrame({"timestamp": timestamps, "load_kw": np.full(8760, 100.0)}).to_csv(
        loads_path, index=False
    )

    pv_path = tmp_path / "pv.csv"
    pd.DataFrame({"timestamp": timestamps, "pv_kw": np.full(8760, 50.0)}).to_csv(
        pv_path, index=False
    )

    weather_path = tmp_path / "weather.csv"
    pd.DataFrame({
        "timestamp": timestamps,
        "irradiance_wm2": np.full(8760, 500.0),
        "temperature_c": np.full(8760, 30.0),
    }).to_csv(weather_path, index=False)

    return PVBESSConfig(
        simulation=SimulationConfig(site="industrial_load", objective="cost_reduction"),
        bess=BESSConfig(capacity_kwh=1000.0, power_kw=250.0),
        pv=PVConfig(capacity_kwp=500.0),
        tariff=TariffConfig(mode="flat", flat_rate_omr_per_kwh=0.025),
        data=DataPathsConfig(
            loads=str(loads_path),
            pv_generation=str(pv_path),
            weather=str(weather_path),
            outputs=str(tmp_path / "outputs"),
        ),
    )
