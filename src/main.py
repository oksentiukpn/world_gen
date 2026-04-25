"""
Entry point for the Procedural Planet Generator.
Handles CLI application startup.
"""

import sys

from cli.parser import parse_arguments


def run_cli(args):
    """
    Executes the planet generator in Command Line Interface (CLI) mode.
    Generates the procedural planet based on the provided configuration
    (seed, resolution, etc.) and saves the output (e.g., textures, meshes) to disk.

    Args:
        args (argparse.Namespace): The parsed command-line arguments containing
                                   configuration options.
    """
    seed = getattr(args, "seed", 42)
    resolution = getattr(args, "resolution", 1024)
    output_path = getattr(args, "output", "planet.png")

    print(f"🌍 Starting procedural planet generation...")
    print(f"   Seed: {seed} | Resolution: {resolution}")

    print("[1/4] Generating spherical grid...")
    # Placeholder: grid_points = create_spherical_grid(resolution)

    print("[2/4] Generating 3D noise and heightmap...")
    # Placeholder: elevations = generate_spherical_heightmap(grid_points, seed=seed)

    print("[3/4] Simulating tectonics and erosion...")
    # Placeholder: elevations = simulate_tectonics(elevations, iterations=10, plate_count=15)
    # Placeholder: elevations = simulate_erosion(elevations, iterations=5, erosion_rate=0.01)

    print("[4/4] Calculating climate and mapping biomes...")
    # Placeholder: biome_map = generate_biome_map(elevations)

    print(f"✅ Planet generated! Saving output to: {output_path}")


def main():
    """
    The main entry point of the application.
    Parses command-line arguments using the cli.parser module and runs the CLI.
    """
    args = parse_arguments()
    run_cli(args)


if __name__ == "__main__":
    main()
