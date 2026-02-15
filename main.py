import argparse
import os
import sys
import time

from Application.Config import Config
from Application.ContourExctractor import ContourExtractor
from Application.Exporter import Exporter
from Application.HeatMap import HeatMap
from Application.Importer import Importer
from Application.LayerFactory import LayerFactory
from Application.LayerManager import LayerManager
from Application.Logger import get_logger, setup_logger
from Application.VideoReader import VideoReader

# Setup logging
setup_logger()
logger = get_logger(__name__)


def main(config: Config) -> int:
    """
    Main processing pipeline for video summarization.

    Args:
        config: Configuration object with processing parameters

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    start_total = time.time()

    try:
        # Check if cached data exists
        cache_path = config["cachePath"] + "_layers.txt"
        if os.path.exists(cache_path):
            logger.info(f"Loading cached data from {cache_path}")
            layers, contours, masks = Importer(config).import_raw_data()
            layers = LayerFactory(config).extract_layers(contours, masks)
        else:
            logger.info("Extracting contours from video...")
            contours, masks = ContourExtractor(config).extract_contours()
            logger.info("Extracting layers from contours...")
            layers = LayerFactory(config).extract_layers(contours, masks)

        logger.info("Cleaning layers...")
        layer_manager = LayerManager(config, layers)
        layer_manager.clean_layers()

        # Check if we have any layers to process
        if len(layer_manager.layers) == 0:
            logger.error("No layers found to process. Exiting.")
            return 1

        # Generate heatmap
        logger.info("Generating heatmap...")
        heatmap = HeatMap(
            config["w"], config["h"], [contour for layer in layer_manager.layers for contour in layer.bounds], 1920 / config["resizeWidth"]
        )
        heatmap.show_image()

        # Export results
        logger.info(f"Exporting {len(contours)} Contours and {len(layer_manager.layers)} Layers")
        Exporter(config).export(layer_manager.layers, contours, masks, raw=True, overlayed=True)

        total_time = time.time() - start_total
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        return 0

    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract movement from static camera recording",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input_video.mp4 output_dir
  %(prog)s input_video.mp4 output_dir custom_config.json
        """,
    )
    parser.add_argument("input", metavar="input_file", type=str, help="Input video file to extract movement from")
    parser.add_argument(
        "output",
        metavar="output_dir",
        type=str,
        nargs="?",
        default="output",
        help="Output directory to save results and cached files (default: output)",
    )
    parser.add_argument("config", metavar="config", type=str, nargs="?", default=None, help="Path to configuration JSON file (optional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging level
    if args.verbose:
        setup_logger(level=10)  # DEBUG level

    try:
        # Load configuration
        config = Config(args.config)

        # Resolve paths
        input_path = os.path.join(os.path.dirname(__file__), args.input)
        output_path = os.path.join(os.path.dirname(__file__), args.output)

        # Validate input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            sys.exit(1)

        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        file_name = input_path.split("/")[-1]

        # Configure paths
        config["inputPath"] = input_path
        config["outputPath"] = os.path.join(output_path, file_name)
        config["cachePath"] = os.path.join(output_path, file_name.split(".")[0])

        # Get video dimensions
        logger.info("Reading video dimensions...")
        config["w"], config["h"] = VideoReader(config).get_wh()

        # Run main processing
        exit_code = main(config)
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.warning("Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
