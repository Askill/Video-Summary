"""Tests for Config module."""

import json
import os
import tempfile

import pytest

from Application.Config import Config


class TestConfig:
    """Test suite for Config class."""

    def test_default_config(self):
        """Test that default config is loaded when no file provided."""
        config = Config(None)
        assert config["min_area"] == 300
        assert config["max_area"] == 900000
        assert config["threshold"] == 7

    def test_load_config_from_json_file(self):
        """Test loading config from a JSON file."""
        test_config = {"min_area": 500, "max_area": 1000000, "threshold": 10}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name

        try:
            config = Config(temp_path)
            assert config["min_area"] == 500
            assert config["max_area"] == 1000000
            assert config["threshold"] == 10
        finally:
            os.unlink(temp_path)

    def test_load_config_from_yaml_file(self):
        """Test loading config from a YAML file."""
        test_config_yaml = """
min_area: 600
max_area: 2000000
threshold: 15
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(test_config_yaml)
            temp_path = f.name

        try:
            config = Config(temp_path)
            assert config["min_area"] == 600
            assert config["max_area"] == 2000000
            assert config["threshold"] == 15
        finally:
            os.unlink(temp_path)

    def test_config_with_invalid_file(self):
        """Test that default config is used when file doesn't exist."""
        config = Config("/nonexistent/path/config.json")
        assert config["min_area"] == 300  # Should use defaults

    def test_config_getitem(self):
        """Test __getitem__ method."""
        config = Config(None)
        assert config["min_area"] is not None
        assert config["nonexistent_key"] is None

    def test_config_setitem(self):
        """Test __setitem__ method."""
        config = Config(None)
        config["new_key"] = "new_value"
        assert config["new_key"] == "new_value"

    def test_config_with_malformed_json(self):
        """Test handling of malformed JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json content")
            temp_path = f.name

        try:
            config = Config(temp_path)
            # Should fall back to defaults
            assert config["min_area"] == 300
        finally:
            os.unlink(temp_path)

    def test_config_save_json(self):
        """Test saving config to JSON file."""
        config = Config(None)
        config["test_value"] = 123

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            config.save(temp_path)
            # Load it back and verify
            with open(temp_path, "r") as f:
                loaded = json.load(f)
            assert loaded["test_value"] == 123
        finally:
            os.unlink(temp_path)

    def test_env_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("VIDEO_SUMMARY_MIN_AREA", "999")
        config = Config(None)
        assert config["min_area"] == 999
