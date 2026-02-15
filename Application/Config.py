"""Configuration management for Video Summary application."""

import json
import os
from typing import Any, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from Application.Logger import get_logger

logger = get_logger(__name__)


class Config:
    """
    Configuration management supporting JSON and YAML formats.

    Supports loading configuration from JSON or YAML files, with fallback
    to default values. Also supports environment variable overrides.
    """

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
            config_path: Path to JSON or YAML configuration file.
                        If None or invalid, uses defaults.
                        Supports .json, .yaml, and .yml extensions.
        """
        if config_path and os.path.isfile(config_path):
            logger.info(f"Using supplied configuration at {config_path}")
            try:
                self.c = self._load_config_file(config_path)
            except Exception as e:
                logger.error(f"Failed to parse config file: {e}")
                logger.warning("Falling back to default configuration")
        else:
            logger.info("Using default configuration")

        # Apply environment variable overrides
        self._apply_env_overrides()

        logger.info("Current Configuration:")
        for key, value in self.c.items():
            logger.info(f"  {key}: {value}")

    def _load_config_file(self, config_path: str) -> dict:
        """
        Load configuration from JSON or YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary with configuration values

        Raises:
            ValueError: If file format is not supported
        """
        ext = os.path.splitext(config_path)[1].lower()

        with open(config_path, "r") as file:
            if ext == ".json":
                return json.load(file)
            elif ext in [".yaml", ".yml"]:
                if not YAML_AVAILABLE:
                    raise ValueError("PyYAML is not installed. Install with: pip install pyyaml")
                return yaml.safe_load(file)
            else:
                # Try JSON first, then YAML
                content = file.read()
                file.seek(0)
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if YAML_AVAILABLE:
                        file.seek(0)
                        return yaml.safe_load(file)
                    else:
                        raise ValueError(f"Unsupported config file format: {ext}")

    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        env_prefix = "VIDEO_SUMMARY_"
        for key in self.c.keys():
            env_key = f"{env_prefix}{key.upper()}"
            env_value = os.environ.get(env_key)
            if env_value is not None:
                # Try to convert to appropriate type
                try:
                    # Try integer
                    self.c[key] = int(env_value)
                except ValueError:
                    try:
                        # Try float
                        self.c[key] = float(env_value)
                    except ValueError:
                        # Use as string
                        self.c[key] = env_value
                logger.info(f"Environment override: {key} = {self.c[key]}")

    def __getitem__(self, key: str) -> Any:
        """Get configuration value by key."""
        if key not in self.c:
            return None
        return self.c[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        self.c[key] = value

    def save(self, output_path: str):
        """
        Save current configuration to file.

        Args:
            output_path: Path to save configuration file.
                        Format is determined by extension (.json, .yaml, .yml)
        """
        ext = os.path.splitext(output_path)[1].lower()

        with open(output_path, "w") as file:
            if ext == ".json":
                json.dump(self.c, file, indent=2)
            elif ext in [".yaml", ".yml"]:
                if not YAML_AVAILABLE:
                    raise ValueError("PyYAML is not installed. Install with: pip install pyyaml")
                yaml.dump(self.c, file, default_flow_style=False)
            else:
                # Default to JSON
                json.dump(self.c, file, indent=2)
