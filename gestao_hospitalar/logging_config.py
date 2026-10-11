"""Configuracao de logs operacionais sem dados sensiveis."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "gestao_hospitalar"


def get_logger(module_name: str) -> logging.Logger:
    """Retorna logger configurado para arquivo com rotacao."""
    logger = logging.getLogger(f"{_LOGGER_NAME}.{module_name}")
    root_logger = logging.getLogger(_LOGGER_NAME)

    if not root_logger.handlers:
        log_path = Path(
            os.getenv("GESTAO_LOG_FILE", "logs/gestao_hospitalar.log")
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        level_name = os.getenv("GESTAO_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        root_logger.setLevel(level)
        handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )
        root_logger.addHandler(handler)
        root_logger.propagate = False

    logger.setLevel(root_logger.level)
    return logger
