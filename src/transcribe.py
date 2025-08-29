"""Transcription orchestration module."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


class TranscriptionError(Exception):
    """Custom exception for transcription-related errors."""
    pass


def transcribe(model: str, audio_file: Path, output_dir: Path, 
               model_config: Dict[str, Any]) -> Path:
    """Transcribe an audio file using the specified model."""
    script_name = f'model_{model}.py'
    script_path = Path('src') / 'models' / script_name
    output_file = output_dir / f'{model}_transcription.json'
    
    if not script_path.exists():
        raise TranscriptionError(
            f"Transcription script for model '{model}' not found at '{script_path}'"
        )

    # Prepare command
    command = [
        sys.executable,
        str(script_path),
        '--input_file', str(audio_file),
        '--output_file', str(output_file),
        '--config', json.dumps(model_config)
    ]
    
    print(f"Running transcription for model: {model}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Transcription complete for model: {model}")
        return output_file
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Transcription failed for {model}: {e.stderr if e.stderr else e.stdout}"
        raise TranscriptionError(error_msg)
    except Exception as e:
        raise TranscriptionError(f"Unexpected error during transcription with {model}: {e}")
