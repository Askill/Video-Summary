import json
import os
from typing import Any, Optional

from Application.Logger import get_logger

logger = get_logger(__name__)


class Config:
    c = {
        "min_area": 300,
        "max_area": 900000,
        "threshold": 7,
        "resizeWidth": 700,
        "inputPath": None,
        "outputPath": None,
        "maxLayerLength": 5000,
        "minLayerLength": 40,
        "tolerance": 20,
        "maxLength": None,
        "ttolerance": 60,
        "videoBufferLength": 250,
        "LayersPerContour": 220,
        "avgNum": 10,
    }

    def __init__(self, config_path: Optional[str]):
        """
        Initialize configuration from file or use defaults.

        Args:
            config_path: Path to JSON configuration file. If None or invalid, uses defaults.
        """
        if config_path and os.path.isfile(config_path):
            logger.info(f"Using supplied configuration at {config_path}")
            try:
                with open(config_path) as file:
                    self.c = json.load(file)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to parse config file: {e}")
                logger.warning("Falling back to default configuration")
        else:
            logger.info("Using default configuration")

        logger.info("Current Configuration:")
        for key, value in self.c.items():
            logger.info(f"  {key}: {value}")

    def __getitem__(self, key: str) -> Any:
        if key not in self.c:
            return None
        return self.c[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.c[key] = value
