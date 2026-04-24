"""
Command-line argument parsing module.
Defines the arguments for CLI execution mode and basic config options.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser for the Procedural Planet Generator.
    Sets up available commands, options (like seed, resolution, output format),
    and different execution modes (e.g., CLI vs. Server).

    Returns:
        argparse.ArgumentParser: The configured argument parser instance.
    """
    pass


def parse_arguments(args=None) -> argparse.Namespace:
    """
    Parses command-line arguments and validates the input parameters.
    Can optionally take a list of strings for testing purposes instead of
    reading directly from sys.argv.

    Args:
        args (list of str, optional): A list of arguments to parse. Defaults to None.

    Returns:
        argparse.Namespace: An object containing the parsed arguments and config values.
    """
    pass
