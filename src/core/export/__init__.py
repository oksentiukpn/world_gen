"""
Export package for the Procedural Planet Generator.

Public API (unchanged for all callers):
    export_planet(data: PlanetData, config: ExportConfig) -> None

To add a new export format:
    1. Create a subclass of BaseExporter in its own module (e.g. gltf_exporter.py).
    2. Implement the export(data, config) method.
    3. Add one line to _EXPORTERS below.
"""

from core.config import ExportConfig
from core.export.base import BaseExporter
from core.export.json_exporter import JsonExporter
from core.export.obj_exporter import ObjExporter
from core.export.png_exporter import PngExporter
from core.logger import get_logger
from core.planet_data import PlanetData

logger = get_logger(__name__)

_EXPORTERS: dict[str, type[BaseExporter]] = {
    "png": PngExporter,
    "obj": ObjExporter,
    "json": JsonExporter,
}


def export_planet(data: PlanetData, config: ExportConfig) -> None:
    """
    Dispatches planet export to the appropriate format-specific exporter.

    Args:
        data:   Generated planet data from PlanetGenerator.generate().
        config: Export parameters — format, output path, radius, terrain_scale.

    Raises:
        ValueError: If the requested format has no registered exporter.
    """
    fmt = config.fmt.lower()
    exporter_cls = _EXPORTERS.get(fmt)

    if exporter_cls is None:
        raise ValueError(
            f"Unsupported export format: '{fmt}'. Available: {sorted(_EXPORTERS)}"
        )

    logger.info(f"Dispatching export → {exporter_cls.__name__}")
    exporter_cls().export(data, config)
