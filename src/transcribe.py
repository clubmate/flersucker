import os
import subprocess

def transcribe(model, audio_file, output_dir):
    """
    Transcribes an audio file using the specified model.
    """
    script_path = os.path.join('models', f'{model}.py')
    output_file = os.path.join(output_dir, f'{model}_transcription.json')
    
    if not os.path.exists(script_path):
        raise ValueError(f"Transcription script for model '{model}' not found at '{script_path}'")

    command = [
        'python',
        script_path,
        '--input_file', audio_file,
        '--output_file', output_file
    ]
    
    print(f"Running transcription for model: {model}")
    subprocess.run(command, check=True)
    print(f"Transcription complete for model: {model}")
    
    return output_file
