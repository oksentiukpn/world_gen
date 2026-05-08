"""
Logging configuration module.
Provides a centralized logging setup to replace standard print() statements,
ensuring consistent log formatting and easier debugging across different OS.
"""

import logging
import sys


class ColorFormatter(logging.Formatter):
    """
    Custom formatter to add colors and icons to console logs.
    """

    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[94m",  # Blue
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.CRITICAL: "\033[1m\033[91m",  # Bold Red
    }

    ICONS = {
        logging.DEBUG: "🐛",
        logging.INFO: "ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "💥",
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        icon = self.ICONS.get(record.levelno, "")

        time_str = self.formatTime(record, "%H:%M:%S")

        # Shorten module name for cleaner output (e.g. 'generation.generator' -> 'generator')
        name_str = record.name.split(".")[-1]

        msg = record.getMessage()

        return f"{self.DIM}[{time_str}]{self.RESET} {icon} {color}{name_str}{self.RESET} {self.DIM}→{self.RESET} {msg}"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Creates and configures a logger with the given name.

    Args:
        name (str): The name of the logger (typically __name__ of the calling module).
        level (int): The logging level (default: logging.INFO).

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers if the logger is requested multiple times
    if not logger.handlers:
        logger.setLevel(level)
        # Prevent messages from propagating to parent loggers that also have
        # handlers — avoids duplicate log lines when both a child logger
        # (e.g. core.export.obj_exporter.ObjExporter) and its parent
        # (e.g. core.export) were each given their own handler.
        logger.propagate = False

        # Create console handler for stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Apply the color formatter
        formatter = ColorFormatter()
        console_handler.setFormatter(formatter)

        # Add the configured handler to the logger
        logger.addHandler(console_handler)

    return logger
