#!/usr/bin/env python3
"""
flersucker: A Simple and Elegant Transcription Tool

A Python-based transcription tool for audio and video files (local or YouTube).
Supports multiple transcription models and creates consensus transcriptions.
"""

import sys
import importlib.util
from pathlib import Path

from src.cli import TranscriptionCLI
from src.config import ConfigManager  
from src.workflow import TranscriptionWorkflow


def apply_nemo_patch_on_windows() -> None:
    """
    Automatically patches the nemo_toolkit on Windows to fix signal.SIGKILL issue.
    This function is intended to be run at the start of the application.
    """
    if sys.platform != "win32":
        return

    try:
        spec = importlib.util.find_spec("nemo")
        if spec is None or spec.origin is None:
            return

        nemo_dir = Path(spec.origin).parent
        exp_manager_path = nemo_dir / 'utils' / 'exp_manager.py'

        if not exp_manager_path.exists():
            return

        # Read and patch the file
        content = exp_manager_path.read_text(encoding='utf-8')
        old_line = "rank_termination_signal: signal.Signals = signal.SIGKILL"
        
        if old_line in content:
            new_line = "rank_termination_signal: signal.Signals = signal.SIGTERM"
            new_content = content.replace(old_line, new_line)
            exp_manager_path.write_text(new_content, encoding='utf-8')
            print("Applied patch to nemo_toolkit for Windows compatibility.")

    except Exception as e:
        print(f"Could not apply nemo_toolkit patch: {e}")


def main() -> None:
    """Main entry point for the transcription tool."""
    # Apply Windows patch if needed
    apply_nemo_patch_on_windows()
    
    # Parse command line arguments
    cli = TranscriptionCLI()
    args = cli.parse_args()
    
    # Validate arguments
    if not cli.validate_args(args):
        sys.exit(1)
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    
    # Create and run workflow
    workflow = TranscriptionWorkflow(config_manager, verbose=args.verbose)
    workflow.run(
        input_path=args.input,
        models=args.models,
        output_base_dir=args.output_dir,
        create_consensus_flag=not args.no_consensus
    )


if __name__ == "__main__":
    main()
