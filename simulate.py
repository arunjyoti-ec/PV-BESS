"""
simulate.py — PV-BESS simulation entrypoint.

Usage:
    python simulate.py --config data/config.yaml
    python simulate.py --config data/config.yaml --dry-run
    python simulate.py --config data/config.yaml --log-level DEBUG
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Ensure project root is on the path when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import PVBESSConfig, load_config
from logger import setup_logging
from validators import (
    check_energy_balance,
    check_power_bounds,
    check_soc,
    load_csv,
    validate_load_profile,
    validate_pv_generation,
    validate_weather,
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the PV-BESS simulation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/config.yaml"),
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and data inputs, then exit without simulating",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional path to write log file (e.g. logs/run.log)",
    )
    return parser.parse_args()


def load_and_validate_data(cfg: PVBESSConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all input CSVs and run validation checks."""
    logger.info("Loading and validating input data...")

    load_df = validate_load_profile(
        load_csv(cfg.data.loads, label="load profile")
    )
    pv_df = validate_pv_generation(
        load_csv(cfg.data.pv_generation, label="PV generation")
    )
    weather_df = validate_weather(
        load_csv(cfg.data.weather, label="weather")
    )

    # Check all datasets cover the same time range
    for name, df in [("PV generation", pv_df), ("weather", weather_df)]:
        if not df["timestamp"].iloc[0] == load_df["timestamp"].iloc[0]:
            logger.warning(
                "%s starts at %s but load profile starts at %s — check alignment.",
                name,
                df["timestamp"].iloc[0],
                load_df["timestamp"].iloc[0],
            )

    logger.info(
        "Data loaded — %d timesteps, %s to %s",
        len(load_df),
        load_df["timestamp"].iloc[0],
        load_df["timestamp"].iloc[-1],
    )
    return load_df, pv_df, weather_df


def run_simulation(
    cfg: PVBESSConfig,
    load_df: pd.DataFrame,
    pv_df: pd.DataFrame,
    weather_df: pd.DataFrame,  # noqa: ARG001 — reserved for temperature-corrected PV dispatch
) -> list[dict[str, float]]:
    """
    Core simulation loop — placeholder for bess_model integration.

    Replace the body of this function with your actual BESS dispatch logic.
    Validators check_soc(), check_power_bounds(), and check_energy_balance()
    are called at every timestep to catch dispatch errors early.
    """
    logger.info(
        "Starting simulation — site=%s, objective=%s",
        cfg.simulation.site,
        cfg.simulation.objective,
    )

    soc = cfg.bess.soc_initial
    timestep_h = cfg.simulation.timestep_minutes / 60.0
    results: list[dict[str, float]] = []

    for step, (_, load_row) in enumerate(load_df.iterrows()):
        load_kw = float(load_row["load_kw"])
        pv_kw = float(pv_df.iloc[step]["pv_kw"])

        # --- Placeholder dispatch logic ---
        # Replace this with your real optimiser/RL/LP dispatch
        net_kw = load_kw - pv_kw
        bess_kw = max(-cfg.bess.power_kw, min(cfg.bess.power_kw, net_kw))

        # Residual demand met by (or exported to) the grid
        grid_kw = load_kw - pv_kw - bess_kw

        # Efficiency-aware SOC update
        if bess_kw >= 0:  # discharging
            delta_soc = -(bess_kw * timestep_h) / (cfg.bess.efficiency_discharge * cfg.bess.capacity_kwh)
        else:  # charging
            delta_soc = -(bess_kw * cfg.bess.efficiency_charge * timestep_h) / cfg.bess.capacity_kwh
        soc = max(cfg.bess.soc_min, min(cfg.bess.soc_max, soc + delta_soc))

        # Physical sanity checks at every timestep
        check_soc(soc, cfg.bess.soc_min, cfg.bess.soc_max, step=step)
        check_power_bounds(bess_kw, cfg.bess.power_kw, step=step)
        check_energy_balance(load_kw, pv_kw, bess_kw, grid_kw, timestep_h, step=step)

        results.append({"step": step, "soc": soc, "bess_kw": bess_kw, "grid_kw": grid_kw})

        if step % 100 == 0:
            logger.debug("Step %d — SOC=%.2f, BESS=%.2f kW, grid=%.2f kW", step, soc, bess_kw, grid_kw)

    logger.info("Simulation complete — %d timesteps processed", len(results))
    return results


def save_results(results: list[dict], output_dir: Path) -> None:
    import json
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "simulation_results.json"
    try:
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info("Results saved to %s", out_path.resolve())
    except OSError as exc:
        logger.error("Failed to save results to %s: %s", out_path, exc)
        raise


def main() -> int:
    args = parse_args()
    setup_logging(level=args.log_level, log_file=args.log_file)

    try:
        cfg = load_config(args.config)
    except Exception as exc:
        logger.error("Configuration error: %s", exc)
        return 1

    # Honour --dry-run from CLI or config
    if args.dry_run or cfg.simulation.dry_run:
        logger.info("Dry-run mode — loading and validating data only.")
        try:
            load_and_validate_data(cfg)
            logger.info("Dry-run complete — all inputs are valid.")
        except Exception as exc:
            logger.error("Dry-run validation failed: %s", exc)
            return 1
        return 0

    try:
        load_df, pv_df, weather_df = load_and_validate_data(cfg)
        results = run_simulation(cfg, load_df, pv_df, weather_df)
        save_results(results, Path(cfg.data.outputs))
    except FileNotFoundError as exc:
        logger.error("Missing file: %s", exc)
        return 1
    except ValueError as exc:
        logger.error("Data or simulation error: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error during simulation: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
