import pytest
from src.cli.parser import create_parser, parse_arguments


def test_create_parser():
    parser = create_parser()
    assert parser is not None
    assert parser.description == "🌍 Procedural Planet Generator CLI"


def test_parse_arguments_defaults():
    args = parse_arguments([])
    assert args.seed == 67
    assert args.subdivisions == 5
    assert args.radius == 2.0
    assert args.format == "obj"
    assert args.output == "planet.png"


def test_parse_arguments_custom():
    args = parse_arguments(
        [
            "--seed",
            "123",
            "--subdivisions",
            "3",
            "--radius",
            "1.5",
            "--format",
            "json",
            "--output",
            "test.json",
        ]
    )
    assert args.seed == 123
    assert args.subdivisions == 3
    assert args.radius == 1.5
    assert args.format == "json"
    assert args.output == "test.json"


def test_parse_arguments_invalid_choices():
    with pytest.raises(SystemExit):
        parse_arguments(["--subdivisions", "10"])

    with pytest.raises(SystemExit):
        parse_arguments(["--format", "xml"])
