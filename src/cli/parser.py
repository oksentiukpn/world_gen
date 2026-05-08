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
    parser = argparse.ArgumentParser(
        description="🌍 Procedural Planet Generator CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ── Basic Options ────────────────────────────────────────────────────────

    basic_group = parser.add_argument_group("Basic Planet Settings")

    basic_group.add_argument(
        "--seed",
        type=int,
        default=67,
        help="Master seed for all noise and random operations.",
    )

    basic_group.add_argument(
        "--subdivisions",
        type=int,
        default=5,
        choices=range(1, 10),
        metavar="[1-9]",
        help=(
            "Icosphere subdivision level controlling mesh detail. "
            "Warning: levels 8-9 are slow and produce very large files."
        ),
    )

    basic_group.add_argument(
        "--radius",
        type=float,
        default=2.0,
        help="Physical radius of the planet.",
    )

    # ── Tectonics ────────────────────────────────────────────────────────────

    tectonics_group = parser.add_argument_group("Tectonics Settings")

    tectonics_group.add_argument(
        "--plate-iterations",
        type=int,
        default=4,
        help="Number of iterations for tectonic plate simulation.",
    )

    tectonics_group.add_argument(
        "--plate-count",
        type=int,
        default=40,
        help="Number of tectonic plates generated.",
    )

    tectonics_group.add_argument(
        "--range-radius",
        type=float,
        default=10.0,
        help="Radius of the range effect for tectonics.",
    )

    tectonics_group.add_argument(
        "--range-amplitude",
        type=float,
        default=1.0,
        help="Amplitude of the tectonic range effect.",
    )

    # ── 3D Noise (fBm) ───────────────────────────────────────────────────────

    noise_group = parser.add_argument_group("3D Noise (fBm) Settings")

    noise_group.add_argument(
        "--noise-scale",
        type=float,
        default=1.0,
        help="Global scale of the 3D noise.",
    )

    noise_group.add_argument(
        "--octaves",
        type=int,
        default=5,
        help="Number of noise octaves for details.",
    )

    noise_group.add_argument(
        "--persistence",
        type=float,
        default=0.4,
        help="Amplitude multiplier per octave.",
    )

    noise_group.add_argument(
        "--lacunarity",
        type=float,
        default=2.0,
        help="Frequency multiplier per octave.",
    )

    noise_group.add_argument(
        "--amplitude",
        type=float,
        default=30.0,
        help="Overall amplitude of the noise.",
    )

    # ── Environment ──────────────────────────────────────────────────────────

    env_group = parser.add_argument_group("Environment Settings")

    env_group.add_argument(
        "--water-level",
        type=float,
        default=0.325,
        help="Minimum level of water (floods terrain below this).",
    )

    env_group.add_argument(
        "--sharpness-strength",
        type=float,
        default=4.0,
        help="Strength of terrain sharpness (ridges).",
    )

    # ── Export ─────────────────────────────────────────────────────────────────

    export_group = parser.add_argument_group("Export Settings")

    export_group.add_argument(
        "--format",
        type=str,
        choices=["png", "obj", "json"],
        default="obj",
        help="Output format for the generated planet.",
    )

    export_group.add_argument(
        "--output",
        type=str,
        default="planet.png",
        help="Output file path.",
    )

    return parser


def parse_arguments(args=None) -> argparse.Namespace:
    """
    Parses command-line arguments and validates the input parameters.

    Args:
        args (list of str, optional): A list of arguments to parse. Defaults to None.

    Returns:
        argparse.Namespace: An object containing the parsed arguments and config values.
    """
    parser = create_parser()
    return parser.parse_args(args)
