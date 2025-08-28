import argparse
import os
import yaml
import sys
import importlib.util
from src.download import download_youtube, extract_audio
from src.transcribe import transcribe
from src.consensus import create_consensus
from src.utils import create_output_directory

def apply_nemo_patch_on_windows():
    """
    Automatically patches the nemo_toolkit on Windows to fix an issue with 'signal.SIGKILL'.
    This function is intended to be run at the start of the application.
    """
    if sys.platform != "win32":
        return

    try:
        spec = importlib.util.find_spec("nemo")
        if spec is None or spec.origin is None:
            return

        nemo_dir = os.path.dirname(spec.origin)
        exp_manager_path = os.path.join(nemo_dir, 'utils', 'exp_manager.py')

        if not os.path.exists(exp_manager_path):
            return

        with open(exp_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()

        old_line = "rank_termination_signal: signal.Signals = signal.SIGKILL"
        if old_line in content:
            new_line = "rank_termination_signal: signal.Signals = signal.SIGTERM"
            new_content = content.replace(old_line, new_line)
            
            with open(exp_manager_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Applied patch to nemo_toolkit for Windows compatibility.")

    except Exception as e:
        print(f"Could not apply nemo_toolkit patch: {e}")


def main():
    apply_nemo_patch_on_windows()
    
    parser = argparse.ArgumentParser(description="Transcription tool for audio and video files.")
    parser.add_argument("input", help="Path to a local file or a YouTube URL.")
    parser.add_argument("--models", nargs="+", help="Transcription models to use.", default=[])
    parser.add_argument("--config", help="Path to a config file.", default="config.yaml")
    args = parser.parse_args()

    # Load config
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # Determine models to use
    models = args.models or config.get("models", [])
    if not models:
        # Prompt user if no models are specified
        print("Available models: whisper, whisperx, faster_whisper, parakeet, canary")
        models_input = input("Which model(s) do you want to use? (space-separated): ")
        models = models_input.split()

    # Create output directory
    output_dir = create_output_directory(args.input)
    print(f"Output will be saved in: {output_dir}")

    # Handle input
    input_path = args.input
    yt_config = config.get("youtube_download", {})
    video_quality = yt_config.get("video_quality", "best[ext=mp4]/best")
    audio_config = yt_config.get("audio_extraction", {})

    if "youtube.com" in input_path or "youtu.be" in input_path:
        print("Downloading from YouTube...")
        video_path = download_youtube(input_path, output_dir, quality=video_quality)
        print("Extracting audio from video...")
        audio_file = extract_audio(video_path, output_dir, audio_config=audio_config)
    elif input_path.endswith(('.mp4')):
        print("Extracting audio from video...")
        # copy the file to the output directory
        import shutil
        shutil.copy(input_path, output_dir)
        video_path = os.path.join(output_dir, os.path.basename(input_path))
        audio_file = extract_audio(video_path, output_dir, audio_config=audio_config)
    else:
        audio_file = input_path
        # copy the file to the output directory
        import shutil
        shutil.copy(audio_file, output_dir)
        audio_file = os.path.join(output_dir, os.path.basename(audio_file))


    # Run transcription
    transcripts = []
    model_configs = config.get("model_configs", {})
    for model in models:
        try:
            model_config = model_configs.get(model, {})
            transcript_file = transcribe(model, audio_file, output_dir, model_config)
            transcripts.append(transcript_file)
        except Exception as e:
            print(f"Error during transcription with {model}: {e}")

    # Create consensus
    if len(transcripts) > 1:
        print("Creating consensus transcription...")
        consensus_output = os.path.join(output_dir, "consensus.json")
        create_consensus(transcripts, consensus_output)

if __name__ == "__main__":
    main()
