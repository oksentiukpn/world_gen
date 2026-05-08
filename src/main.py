"""
Entry point for the Procedural Planet Generator.
Handles CLI application startup.
"""

import sys

from cli.parser import parse_arguments
from core.config import ExportConfig, PlanetConfig
from core.export import export_planet
from generation.generator import PlanetGenerator

# ANSI escape codes for beautiful output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"


def print_header():
    header = f"""
{BOLD}{CYAN}🌍 Procedural Planet Generator CLI{RESET}
{CYAN}=================================={RESET}
"""
    print(header)


def run_cli(args):
    """
    Executes the planet generator in Command Line Interface (CLI) mode.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    """
    print_header()

    planet_config = PlanetConfig(
        seed=args.seed,
        subdivisions=args.subdivisions,
        radius=args.radius,
        noise_scale=args.noise_scale,
        octaves=args.octaves,
        persistence=args.persistence,
        lacunarity=args.lacunarity,
        amplitude=args.amplitude,
        water_level=args.water_level,
        sharpness_strength=args.sharpness_strength,
        plate_iterations=args.plate_iterations,
        plate_count=args.plate_count,
        range_radius=args.range_radius,
        range_amplitude=args.range_amplitude,
    )

    export_config = ExportConfig(
        fmt=args.format,
        output_path=args.output,
    )

    print(f"{BOLD}{BLUE}[*] Engine Settings:{RESET}")
    print(f"    {BOLD}Seed:{RESET}         {YELLOW}{planet_config.seed}{RESET}")
    print(f"    {BOLD}Subdivisions:{RESET} {YELLOW}{planet_config.subdivisions}{RESET}")
    print(f"    {BOLD}Radius:{RESET}       {YELLOW}{planet_config.radius}{RESET}")
    print(
        f"    {BOLD}Noise Scale:{RESET}  {YELLOW}{planet_config.noise_scale}{RESET} (Oct: {planet_config.octaves}, Per: {planet_config.persistence})"
    )
    print(
        f"    {BOLD}Tectonics:{RESET}    {YELLOW}{planet_config.plate_count}{RESET} plates, {YELLOW}{planet_config.plate_iterations}{RESET} iterations"
    )

    print(f"\n{BOLD}{BLUE}[*] Export Settings:{RESET}")
    print(f"    {BOLD}Format:{RESET}       {MAGENTA}{export_config.fmt.upper()}{RESET}")
    print(
        f"    {BOLD}Output:{RESET}       {MAGENTA}{export_config.output_path}{RESET}\n"
    )

    if planet_config.subdivisions >= 8:
        print(
            f"{BOLD}{YELLOW}⚠️  WARNING:{RESET} Subdivisions={planet_config.subdivisions} will produce "
            f"~{10 * 4**planet_config.subdivisions + 2:,} vertices.\n"
            f"Expect slow generation and a large output file.\n"
        )

    generator = PlanetGenerator(planet_config)

    print(f"{BOLD}{CYAN}[~] Generating planet data...{RESET}")
    planet_data = generator.generate()

    print(f"{BOLD}{CYAN}[~] Saving file to {export_config.output_path}...{RESET}")
    export_planet(planet_data, export_config)

    print(f"\n{BOLD}{GREEN}✅ Generation and export fully complete!{RESET}")


def main():
    """
    The main entry point of the application.
    Parses command-line arguments using the cli.parser module and runs the CLI.
    """
    args = parse_arguments()
    try:
        run_cli(args)
    except KeyboardInterrupt:
        print(f"\n{BOLD}{YELLOW}⚠️  Generation cancelled by user.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
