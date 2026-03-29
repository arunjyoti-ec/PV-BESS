"""
config.py — PV-BESS configuration loader and validator.

Validates config.yaml at startup using Pydantic v2.
Raises descriptive errors immediately if any field is missing or out of range.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class BESSConfig(BaseModel):
    capacity_kwh: float = Field(..., gt=0, description="Usable battery capacity in kWh")
    power_kw: float = Field(..., gt=0, description="Max charge/discharge power in kW")
    soc_min: float = Field(0.1, ge=0.0, le=1.0, description="Minimum state of charge (0–1)")
    soc_max: float = Field(0.9, ge=0.0, le=1.0, description="Maximum state of charge (0–1)")
    soc_initial: float = Field(0.5, ge=0.0, le=1.0, description="Initial SOC at simulation start")
    efficiency_charge: float = Field(0.95, gt=0.0, le=1.0, description="Charging round-trip efficiency")
    efficiency_discharge: float = Field(0.95, gt=0.0, le=1.0, description="Discharge efficiency")
    degradation_rate_per_cycle: float = Field(
        0.0001, ge=0.0, le=0.01,
        description="Capacity loss per cycle (fraction)"
    )

    @model_validator(mode="after")
    def soc_bounds_consistent(self) -> "BESSConfig":
        if self.soc_min >= self.soc_max:
            raise ValueError(
                f"soc_min ({self.soc_min}) must be strictly less than soc_max ({self.soc_max})"
            )
        if not (self.soc_min <= self.soc_initial <= self.soc_max):
            raise ValueError(
                f"soc_initial ({self.soc_initial}) must be between "
                f"soc_min ({self.soc_min}) and soc_max ({self.soc_max})"
            )
        return self


class PVConfig(BaseModel):
    capacity_kwp: float = Field(..., gt=0, description="Installed PV capacity in kWp")
    degradation_rate_annual: float = Field(
        0.005, ge=0.0, le=0.05,
        description="Annual PV degradation rate (fraction)"
    )
    panel_efficiency: float = Field(0.20, gt=0.0, le=1.0, description="Panel efficiency (0–1)")
    temperature_coefficient: float = Field(
        -0.004, ge=-0.01, le=0.0,
        description="Power temperature coefficient (%/°C, typically negative)"
    )


class TariffConfig(BaseModel):
    mode: Literal["crt_2025", "flat", "tou"] = Field(
        ..., description="Tariff mode: crt_2025 | flat | tou"
    )
    flat_rate_omr_per_kwh: float | None = Field(
        None, ge=0.0,
        description="Used only when mode=flat"
    )
    tariff_file: str | None = Field(
        None, description="Path to CRT/TOU tariff CSV (used when mode=crt_2025 or tou)"
    )

    @model_validator(mode="after")
    def tariff_file_required(self) -> "TariffConfig":
        if self.mode in ("crt_2025", "tou") and not self.tariff_file:
            raise ValueError(
                f"tariff_file must be provided when mode='{self.mode}'"
            )
        if self.mode == "flat" and self.flat_rate_omr_per_kwh is None:
            raise ValueError("flat_rate_omr_per_kwh must be provided when mode='flat'")
        return self


class SimulationConfig(BaseModel):
    site: Literal["industrial_load", "solar_pv_plant"] = Field(
        ..., description="Site type: industrial_load | solar_pv_plant"
    )
    timestep_minutes: int = Field(60, ge=1, le=60, description="Simulation timestep in minutes")
    project_lifetime_years: int = Field(25, ge=1, le=50, description="Project lifetime for NPV/IRR")
    discount_rate: float = Field(0.08, ge=0.0, le=1.0, description="Discount rate for NPV (0–1)")
    objective: Literal["cost_reduction", "peak_shaving", "self_consumption", "export_revenue"] = Field(
        ..., description="Primary optimisation objective"
    )
    dry_run: bool = Field(False, description="If true, validate config and exit without simulating")

    @field_validator("timestep_minutes")
    @classmethod
    def timestep_divides_hour(cls, v: int) -> int:
        if 60 % v != 0:
            raise ValueError(
                f"timestep_minutes ({v}) must divide 60 evenly (e.g. 1, 5, 10, 15, 30, 60)"
            )
        return v


class DataPathsConfig(BaseModel):
    loads: str = Field(..., description="Path to load profile CSV")
    pv_generation: str = Field(..., description="Path to PV generation CSV")
    weather: str = Field(..., description="Path to weather/irradiance CSV")
    outputs: str = Field("data/outputs", description="Directory for simulation outputs")

    @model_validator(mode="after")
    def input_files_exist(self) -> "DataPathsConfig":
        for field_name in ("loads", "pv_generation", "weather"):
            path = Path(getattr(self, field_name))
            if not path.exists():
                raise FileNotFoundError(
                    f"Data file not found for '{field_name}': {path.resolve()}\n"
                    f"  → Place a CSV at that path or update config.yaml"
                )
        return self


class PVBESSConfig(BaseModel):
    """Root configuration model for the PV-BESS simulation."""
    simulation: SimulationConfig
    bess: BESSConfig
    pv: PVConfig
    tariff: TariffConfig
    data: DataPathsConfig


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path) -> PVBESSConfig:
    """
    Load and validate config.yaml, raising clear errors on any issue.

    Parameters
    ----------
    config_path : str or Path
        Path to the YAML configuration file.

    Returns
    -------
    PVBESSConfig
        Fully validated configuration object.

    Raises
    ------
    FileNotFoundError
        If config_path does not exist.
    yaml.YAMLError
        If the YAML is malformed.
    pydantic.ValidationError
        If any field is missing, wrong type, or out of range.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path.resolve()}\n"
            f"  → Copy data/config.yaml.example to data/config.yaml and edit it."
        )

    logger.info("Loading config from: %s", config_path)

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise yaml.YAMLError(
            f"Malformed YAML in {config_path}: {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"config.yaml must be a YAML mapping (dict) at the top level, got {type(raw).__name__}"
        )

    config = PVBESSConfig(**raw)
    logger.info(
        "Config validated — site=%s, objective=%s, timestep=%dmin",
        config.simulation.site,
        config.simulation.objective,
        config.simulation.timestep_minutes,
    )
    return config
