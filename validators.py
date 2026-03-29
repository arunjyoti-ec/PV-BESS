"""
validators.py — Input data validation and physical sanity checks for PV-BESS.

Call these functions immediately after loading any CSV/DataFrame.
They raise descriptive errors rather than letting bad data propagate silently.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Required column schemas
# ---------------------------------------------------------------------------

LOAD_SCHEMA: dict[str, str] = {
    "timestamp": "datetime64[ns]",
    "load_kw": "float64",
}

PV_SCHEMA: dict[str, str] = {
    "timestamp": "datetime64[ns]",
    "pv_kw": "float64",
}

WEATHER_SCHEMA: dict[str, str] = {
    "timestamp": "datetime64[ns]",
    "irradiance_wm2": "float64",
    "temperature_c": "float64",
}


# ---------------------------------------------------------------------------
# Generic CSV loader with error handling
# ---------------------------------------------------------------------------

def load_csv(path: str | Path, label: str = "data") -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame with descriptive error messages.

    Parameters
    ----------
    path : str or Path
        Path to the CSV file.
    label : str
        Human-readable label for error messages (e.g. 'load profile').

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is empty or cannot be parsed as CSV.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"[{label}] CSV not found: {path.resolve()}\n"
            f"  → Check the path in config.yaml under data.{label.replace(' ', '_')}"
        )

    try:
        df = pd.read_csv(path, parse_dates=["timestamp"])
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"[{label}] Could not parse CSV at {path}: {exc}\n"
            f"  → Check the file is valid UTF-8 CSV with a header row."
        ) from exc
    except ValueError as exc:
        # parse_dates may raise if 'timestamp' column is missing
        raise ValueError(
            f"[{label}] CSV at {path} is missing a 'timestamp' column.\n"
            f"  → See data/sample/README.md for the required format."
        ) from exc

    if df.empty:
        raise ValueError(
            f"[{label}] CSV at {path} is empty (0 rows).\n"
            f"  → Provide at least one row of data."
        )

    logger.info("[%s] Loaded %d rows from %s", label, len(df), path.name)
    return df


# ---------------------------------------------------------------------------
# Schema validators
# ---------------------------------------------------------------------------

def _validate_schema(df: pd.DataFrame, schema: dict[str, str], label: str) -> pd.DataFrame:
    """
    Check that all required columns exist and cast to expected dtypes.
    """
    missing = [col for col in schema if col not in df.columns]
    if missing:
        raise ValueError(
            f"[{label}] Missing required columns: {missing}\n"
            f"  Expected columns: {list(schema.keys())}\n"
            f"  Found columns:    {list(df.columns)}"
        )

    for col, dtype in schema.items():
        if col == "timestamp":
            continue  # already parsed by load_csv
        try:
            df[col] = df[col].astype(dtype)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"[{label}] Column '{col}' could not be cast to {dtype}: {exc}"
            ) from exc

    return df


def validate_load_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Validate industrial load profile DataFrame."""
    df = _validate_schema(df, LOAD_SCHEMA, "load profile")
    _check_no_nulls(df, ["load_kw"], "load profile")
    _check_non_negative(df, "load_kw", "load profile")
    _check_timestamps_sorted(df, "load profile")
    logger.debug("[load profile] Validation passed — %d rows", len(df))
    return df


def validate_pv_generation(df: pd.DataFrame) -> pd.DataFrame:
    """Validate solar PV generation DataFrame."""
    df = _validate_schema(df, PV_SCHEMA, "PV generation")
    _check_no_nulls(df, ["pv_kw"], "PV generation")
    _check_non_negative(df, "pv_kw", "PV generation")
    _check_timestamps_sorted(df, "PV generation")
    logger.debug("[PV generation] Validation passed — %d rows", len(df))
    return df


def validate_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Validate weather/irradiance DataFrame."""
    df = _validate_schema(df, WEATHER_SCHEMA, "weather")
    _check_no_nulls(df, ["irradiance_wm2", "temperature_c"], "weather")
    _check_non_negative(df, "irradiance_wm2", "weather")
    _check_range(df, "temperature_c", -10.0, 60.0, "weather",
                 hint="Muscat temperatures should be between -10°C and 60°C")
    _check_range(df, "irradiance_wm2", 0.0, 1500.0, "weather",
                 hint="Irradiance above 1500 W/m² is physically implausible")
    _check_timestamps_sorted(df, "weather")
    logger.debug("[weather] Validation passed — %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Physical sanity checks for simulation state
# ---------------------------------------------------------------------------

def check_soc(soc: float, soc_min: float, soc_max: float, step: int | None = None) -> None:
    """
    Assert that state of charge is within configured bounds.

    Parameters
    ----------
    soc : float
        Current SOC (0–1 fraction).
    soc_min, soc_max : float
        Configured SOC bounds.
    step : int, optional
        Simulation timestep index for error context.
    """
    step_info = f" at timestep {step}" if step is not None else ""
    if not (0.0 <= soc <= 1.0):
        raise ValueError(
            f"SOC {soc:.4f} is outside physical bounds [0, 1]{step_info}.\n"
            f"  → Check charge/discharge logic in bess_model/simulate.py"
        )
    if soc < soc_min - 1e-6:
        raise ValueError(
            f"SOC {soc:.4f} fell below soc_min={soc_min}{step_info}.\n"
            f"  → The dispatch algorithm may have over-discharged the battery."
        )
    if soc > soc_max + 1e-6:
        raise ValueError(
            f"SOC {soc:.4f} exceeded soc_max={soc_max}{step_info}.\n"
            f"  → The dispatch algorithm may have over-charged the battery."
        )


def check_power_bounds(power_kw: float, max_power_kw: float, step: int | None = None) -> None:
    """Assert that charge/discharge power does not exceed rated power."""
    step_info = f" at timestep {step}" if step is not None else ""
    if abs(power_kw) > max_power_kw + 1e-6:
        raise ValueError(
            f"BESS power {power_kw:.2f} kW exceeds rated max {max_power_kw:.2f} kW{step_info}.\n"
            f"  → Clamp dispatch commands to [-max_power_kw, max_power_kw]."
        )


def check_energy_balance(
    load_kw: float,
    pv_kw: float,
    bess_kw: float,
    grid_kw: float,
    timestep_h: float,
    step: int | None = None,
    tolerance_kw: float = 0.1,
) -> None:
    """
    Verify power balance: load == pv + bess_discharge + grid_import.

    Signs convention:
        bess_kw  > 0 → discharging (supplying load)
        bess_kw  < 0 → charging (consuming power)
        grid_kw  > 0 → importing from grid
        grid_kw  < 0 → exporting to grid
    """
    imbalance = abs(load_kw - pv_kw - bess_kw - grid_kw)
    if imbalance > tolerance_kw:
        step_info = f" at timestep {step}" if step is not None else ""
        raise ValueError(
            f"Energy balance violation{step_info}: "
            f"load={load_kw:.2f} kW, pv={pv_kw:.2f} kW, "
            f"bess={bess_kw:.2f} kW, grid={grid_kw:.2f} kW → "
            f"imbalance={imbalance:.4f} kW (tolerance={tolerance_kw} kW)"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_no_nulls(df: pd.DataFrame, columns: Sequence[str], label: str) -> None:
    for col in columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            null_idx = df[df[col].isna()].index.tolist()[:5]
            raise ValueError(
                f"[{label}] Column '{col}' has {null_count} NaN value(s). "
                f"First affected rows: {null_idx}\n"
                f"  → Fill or remove NaNs before running the simulation."
            )


def _check_non_negative(df: pd.DataFrame, col: str, label: str) -> None:
    neg_count = (df[col] < 0).sum()
    if neg_count > 0:
        raise ValueError(
            f"[{label}] Column '{col}' has {neg_count} negative value(s). "
            f"Min value: {df[col].min():.4f}\n"
            f"  → '{col}' must be ≥ 0 at all timesteps."
        )


def _check_range(
    df: pd.DataFrame,
    col: str,
    low: float,
    high: float,
    label: str,
    hint: str = "",
) -> None:
    out_of_range = df[(df[col] < low) | (df[col] > high)]
    if not out_of_range.empty:
        logger.warning(
            "[%s] Column '%s' has %d values outside [%.1f, %.1f]. %s",
            label, col, len(out_of_range), low, high, hint,
        )


def _check_timestamps_sorted(df: pd.DataFrame, label: str) -> None:
    if not df["timestamp"].is_monotonic_increasing:
        raise ValueError(
            f"[{label}] 'timestamp' column is not sorted in ascending order.\n"
            f"  → Sort the CSV by timestamp before running the simulation."
        )
    duplicates = df["timestamp"].duplicated().sum()
    if duplicates > 0:
        raise ValueError(
            f"[{label}] 'timestamp' column has {duplicates} duplicate value(s).\n"
            f"  → Remove or aggregate duplicate timestamps."
        )
