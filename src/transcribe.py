import os
import subprocess
import json
import sys

def transcribe(model, audio_file, output_dir, model_config):
    """
    Transcribes an audio file using the specified model.
    """
    script_name = f'model_{model}.py'
    script_path = os.path.join('src', 'models', script_name)
    
    # Use the base name of the audio file for the output filename
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = os.path.join(output_dir, f'{base_name}-{model}.json')
    
    if not os.path.exists(script_path):
        raise ValueError(f"Transcription script for model '{model}' not found at '{script_path}'")

    command = [
        sys.executable,  # Use the same python that is running main.py
        script_path,
        '--input_file', audio_file,
        '--output_file', output_file,
        '--config', json.dumps(model_config)
    ]
    
    print(f"Running transcription for model: {model}")
    subprocess.run(command, check=True)
    print(f"Transcription complete for model: {model}")
    
    return output_file
