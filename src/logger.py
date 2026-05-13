"""Logging configuration for ILNET monitoring platform"""

import logging
import structlog
from pathlib import Path
from src.config import config

# Create logs directory if it doesn't exist
config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Configure standard logging
logging.basicConfig(
    format="%(message)s",
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOGS_DIR / 'ilnet-collector.log'),
    ]
)

# Get logger
logger = structlog.get_logger(__name__)
