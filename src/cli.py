"""CLI interface for the transcription tool."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional


class TranscriptionCLI:
    """Command-line interface for the transcription tool."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Transcription tool for audio and video files.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py audio.wav --models whisper
  python main.py "https://youtube.com/watch?v=..." --models whisper parakeet
  python main.py video.mp4 --config my_config.yaml
  python main.py audio.mp3 --models whisper --output-dir ./results
            """
        )
        
        # Required arguments
        parser.add_argument(
            "input",
            help="Path to a local audio/video file or a YouTube URL."
        )
        
        # Optional arguments
        parser.add_argument(
            "--models", 
            nargs="+", 
            help="Transcription models to use. Available: whisper, whisperx, faster_whisper, parakeet, canary",
            default=[]
        )
        
        parser.add_argument(
            "--config", 
            help="Path to a config file (default: config.yaml)",
            default="config.yaml"
        )
        
        parser.add_argument(
            "--output-dir",
            help="Base output directory (default: output)",
            default="output"
        )
        
        parser.add_argument(
            "--no-consensus",
            action="store_true",
            help="Skip creating consensus when multiple models are used"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="flersucker 1.0.0"
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """Parse command line arguments."""
        return self.parser.parse_args(args)
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """Validate parsed arguments."""
        # Check if input file exists (for local files)
        input_path = Path(args.input)
        if not self._is_url(args.input) and not input_path.exists():
            print(f"Error: Input file '{args.input}' does not exist.")
            return False
        
        # Check if config file exists (if specified and not default)
        if args.config != "config.yaml" and not Path(args.config).exists():
            print(f"Error: Config file '{args.config}' does not exist.")
            return False
        
        return True
    
    def _is_url(self, string: str) -> bool:
        """Check if string is a URL."""
        return string.startswith(('http://', 'https://', 'youtube.com', 'youtu.be'))
    
    def print_help(self) -> None:
        """Print help message."""
        self.parser.print_help()
    
    def error(self, message: str) -> None:
        """Print error message and exit."""
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)