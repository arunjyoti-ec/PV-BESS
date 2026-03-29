"""
logger.py — Structured logging setup for PV-BESS.

Call setup_logging() once at the start of any entrypoint (simulate.py, app.py).
All other modules use: logger = logging.getLogger(__name__)
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: str | Path | None = None,
    rich_console: bool = True,
) -> None:
    """
    Configure application-wide logging for PV-BESS.

    Outputs structured logs to console (with optional rich formatting)
    and optionally to a rotating file.

    Parameters
    ----------
    level : str
        Logging level: DEBUG | INFO | WARNING | ERROR. Default: INFO.
    log_file : str or Path, optional
        If provided, also write logs to this file (rotating, 5MB × 3 backups).
    rich_console : bool
        Use rich library for coloured console output if available. Default True.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: '{level}'. Use DEBUG/INFO/WARNING/ERROR.")

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove any existing handlers (avoid duplicate logs on re-init)
    root.handlers.clear()

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # --- Console handler ---
    console_handler: logging.Handler
    if rich_console:
        try:
            from rich.logging import RichHandler
            console_handler = RichHandler(
                level=numeric_level,
                show_time=True,
                show_path=True,
                rich_tracebacks=True,
            )
            console_handler.setFormatter(logging.Formatter("%(message)s", datefmt=datefmt))
        except ImportError:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root.addHandler(console_handler)

    # --- File handler ---
    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        root.addHandler(file_handler)
        logging.getLogger(__name__).info("File logging active: %s", log_path.resolve())

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "botocore", "boto3", "tensorflow", "torch"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).debug("Logging initialised at level=%s", level)
