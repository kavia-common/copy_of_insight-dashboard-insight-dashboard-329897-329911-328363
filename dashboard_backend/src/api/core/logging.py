from __future__ import annotations

import logging
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Get a module-scoped logger configured by Uvicorn/FastAPI.

    Contract:
      - Inputs: logger name.
      - Outputs: python Logger.
      - Errors: none.
      - Side effects: none.
    """
    return logging.getLogger(name)


def log_kv(logger: logging.Logger, level: int, message: str, **fields: Any) -> None:
    """Log a message with lightweight key=value context.

    We avoid requiring third-party structured logging libraries while still
    providing consistent, searchable context.

    Contract:
      - Inputs: message + fields (must be JSON-serializable-ish).
      - Outputs: none.
      - Errors: never raises (best-effort).
      - Side effects: emits a log record.
    """
    try:
        suffix = " ".join(f"{k}={fields[k]!r}" for k in sorted(fields.keys()))
        logger.log(level, f"{message} {suffix}".rstrip())
    except Exception:
        logger.log(level, message)
