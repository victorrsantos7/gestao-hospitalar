"""Configuracao de logs operacionais sem dados sensiveis."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "gestao_hospitalar"


def get_logger(module_name: str) -> logging.Logger:
    """Retorna logger configurado para arquivo com rotacao (ou saida padrao)."""
    logger = logging.getLogger(f"{_LOGGER_NAME}.{module_name}")
    root_logger = logging.getLogger(_LOGGER_NAME)

    if not root_logger.handlers:
        caminho = os.getenv("GESTAO_LOG_FILE", "logs/gestao_hospitalar.log").strip()
        level_name = os.getenv("GESTAO_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        root_logger.setLevel(level)
        handler: logging.Handler | None = None
        # "-" escolhe a saída padrão (ex.: nuvem, onde os logs ficam no painel).
        if caminho and caminho != "-":
            try:
                log_path = Path(caminho)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                handler = RotatingFileHandler(
                    log_path,
                    maxBytes=5 * 1024 * 1024,
                    backupCount=3,
                    encoding="utf-8",
                )
            except OSError:
                # Pasta sem escrita: o app não pode cair por causa do log.
                handler = None
        if handler is None:
            handler = logging.StreamHandler(sys.stderr)
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
