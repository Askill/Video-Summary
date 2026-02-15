"""Tests for Logger module."""
import logging
import tempfile

from Application.Logger import get_logger, setup_logger


class TestLogger:
    """Test suite for Logger utility functions."""

    def test_setup_logger_default(self):
        """Test setting up logger with default parameters."""
        logger = setup_logger(name="test_logger_1")
        assert logger is not None
        assert logger.name == "test_logger_1"
        assert logger.level == logging.INFO

    def test_setup_logger_with_level(self):
        """Test setting up logger with custom level."""
        logger = setup_logger(name="test_logger_2", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_setup_logger_with_file(self):
        """Test setting up logger with file output."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_file = f.name

        logger = setup_logger(name="test_logger_3", log_file=log_file)
        logger.info("Test message")

        # Verify file was created and has content
        with open(log_file, "r") as f:
            content = f.read()
            assert "Test message" in content

    def test_get_logger(self):
        """Test getting an existing logger."""
        # First create a logger
        setup_logger(name="test_logger_4")

        # Then retrieve it
        logger = get_logger("test_logger_4")
        assert logger is not None
        assert logger.name == "test_logger_4"

    def test_logger_prevents_duplicate_handlers(self):
        """Test that setting up the same logger twice doesn't add duplicate handlers."""
        logger1 = setup_logger(name="test_logger_5")
        handler_count_1 = len(logger1.handlers)

        # Setup the same logger again
        logger2 = setup_logger(name="test_logger_5")
        handler_count_2 = len(logger2.handlers)

        # Should have the same number of handlers
        assert handler_count_1 == handler_count_2
