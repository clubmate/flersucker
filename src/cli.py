"""
Command-line interface for the transcription tool.
"""
import argparse
from typing import Dict, Any


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Transcription tool for audio / video / YouTube playlist (sequential).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py audio.wav --models parakeet
  python main.py https://youtube.com/watch?v=... --models parakeet
  python main.py https://youtube.com/playlist?list=... --playlist-start 5
        """
    )
    
    parser.add_argument(
        "input",
        help="Path to local file or YouTube URL / playlist"
    )
    
    parser.add_argument(
        "--models",
        nargs="+",
        default=[],
        help="Models to use for transcription (default: from config)"
    )
    
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    
    parser.add_argument(
        "--playlist-start",
        type=int,
        default=1,
        help="Start index (1-based) when processing a YouTube playlist (default: 1)"
    )
    
    return parser


def parse_args() -> Dict[str, Any]:
    """Parse command line arguments and return as dictionary."""
    parser = create_parser()
    args = parser.parse_args()
    return vars(args)