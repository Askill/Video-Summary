"""Video Summary Application Package.

This package provides tools for video summarization through contour extraction
and layer-based processing.
"""

__version__ = "0.1.0"
__author__ = "Askill"

# Core imports
from Application.Config import Config
from Application.Layer import Layer

# Import optional components that may have additional dependencies
__all__ = ["Config", "Layer"]

# Try to import video processing components
try:
    from Application.ContourExctractor import ContourExtractor
    from Application.Exporter import Exporter
    from Application.HeatMap import HeatMap
    from Application.Importer import Importer
    from Application.LayerFactory import LayerFactory
    from Application.VideoReader import VideoReader

    __all__.extend(["ContourExtractor", "Exporter", "HeatMap", "Importer", "LayerFactory", "VideoReader"])
except ImportError as e:
    import warnings

    warnings.warn(
        f"Video processing components could not be imported. Missing dependency: {e.name if hasattr(e, 'name') else str(e)}. "
        f"Install with: pip install -r requirements.txt"
    )

# Try to import LayerManager (may require TensorFlow for classification features)
try:
    from Application.LayerManager import LayerManager

    __all__.append("LayerManager")
except ImportError:
    import warnings

    warnings.warn("LayerManager could not be imported. TensorFlow may be required for classification features.")
