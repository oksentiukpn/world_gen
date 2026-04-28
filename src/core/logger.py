"""
Logging configuration module.
Provides a centralized logging setup to replace standard print() statements,
ensuring consistent log formatting and easier debugging across different OS.
"""

import logging
import sys


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

        # Define the logging format: [Time] | [Level] | [Module] | Message
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s | %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add the configured handler to the logger
        logger.addHandler(console_handler)

    return logger
