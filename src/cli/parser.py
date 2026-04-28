"""
Command-line argument parsing module.
Defines the arguments for CLI execution mode and basic config options.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser for the Procedural Planet Generator.

    Returns:
        argparse.ArgumentParser: The configured argument parser instance.
    """
    parser = argparse.ArgumentParser(description="🌍 Procedural Planet Generator CLI")

    # ── Planet generation ──────────────────────────────────────────────────────

    parser.add_argument(
        "--seed",
        type=int,
        default=67,
        help="Seed for procedural generation (default: 67)",
    )

    parser.add_argument(
        "--subdivisions",
        type=int,
        default=5,
        choices=range(1, 10),
        metavar="[1-9]",
        help=(
            "Icosphere subdivision level controlling mesh detail (default: 5). "
            "1=42 verts, 3=642, 5=10242, 7=163842, 9=2621442. "
            "Warning: levels 8-9 are slow and produce very large files."
        ),
    )

    parser.add_argument(
        "--radius",
        type=float,
        default=1.0,
        help=(
            "Physical radius of the planet (default: 1.0). "
            "Controls both the output size AND terrain density: "
            "larger radius → denser, finer terrain features; "
            "smaller radius → coarse, dramatic terrain (asteroid-like)."
        ),
    )

    # ── Export ─────────────────────────────────────────────────────────────────

    parser.add_argument(
        "--format",
        type=str,
        choices=["png", "obj", "json"],
        default="png",
        help="Output format for the generated planet (png, obj, or json) (default: png)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="planet.png",
        help="Output file path (default: planet.png)",
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
