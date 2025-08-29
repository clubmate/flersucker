"""
Transcription module for running model-specific transcription scripts.
"""
import os
import sys
import json
import subprocess
from typing import Dict, Any


def transcribe(model: str, audio_file: str, output_dir: str, model_config: Dict[str, Any]) -> str:
    """
    Transcribe an audio file using the specified model.
    
    Args:
        model: Name of the model to use (must have corresponding model_{model}.py script)
        audio_file: Path to the audio file to transcribe
        output_dir: Directory where the output file will be saved
        model_config: Configuration dictionary for the model
        
    Returns:
        Path to the generated transcript file
        
    Raises:
        ValueError: If the model script is not found
        subprocess.CalledProcessError: If the transcription script fails
    """
    script_name = f'model_{model}.py'
    script_path = os.path.join('src', 'models', script_name)
    
    if not os.path.exists(script_path):
        raise ValueError(f"Transcription script for model '{model}' not found at '{script_path}'")

    # Generate output filename
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = os.path.join(output_dir, f'{base_name}-{model}.json')
    
    # Prepare command to run the model script
    command = [
        sys.executable,  # Use the same python interpreter
        script_path,
        '--input_file', audio_file,
        '--output_file', output_file,
        '--config', json.dumps(model_config)
    ]
    
    print(f"Running transcription for model: {model}")
    
    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"Transcription complete for model: {model}")
        return output_file
    
    except subprocess.CalledProcessError as e:
        print(f"Transcription failed for model {model}: {e}")
        raise
