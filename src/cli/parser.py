"""
Command-line argument parsing module.
Defines the arguments for CLI execution mode and basic config options.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser for the Procedural Planet Generator.
    Sets up available options like seed, resolution, and output format.

    Returns:
        argparse.ArgumentParser: The configured argument parser instance.
    """
    parser = argparse.ArgumentParser(description="🌍 Procedural Planet Generator CLI")

    parser.add_argument(
        "--seed",
        type=int,
        default=67,
        help="Seed for procedural generation (default: 67)",
    )

    parser.add_argument(
        "--resolution",
        type=int,
        default=1024,
        help="Resolution of the generated planet grid (default: 1024)",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["png", "obj"],
        default="png",
        help="Output format for the generated planet (png or obj) (default: png)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="planet.png",
        help="Output file path for the generated textures or data (default: planet.png)",
    )

    return parser


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
    parser = create_parser()
    return parser.parse_args(args)
