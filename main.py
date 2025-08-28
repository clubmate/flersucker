import argparse
import os
import yaml
from src.download import download_youtube, extract_audio
from src.transcribe import transcribe
from src.consensus import create_consensus
from src.utils import create_output_directory

def main():
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
        print("Available models: whisper, whisperx, faster_whisper, parakeet, phi, canary, voxtral") # Add other models later
        models_input = input("Which model(s) do you want to use? (space-separated): ")
        models = models_input.split()

    # Create output directory
    output_dir = create_output_directory(args.input)
    print(f"Output will be saved in: {output_dir}")

    # Handle input
    input_path = args.input
    if "youtube.com" in input_path or "youtu.be" in input_path:
        print("Downloading from YouTube...")
        # Note: download_youtube returns the path to the downloaded file, 
        # but it might be a video file that needs audio extraction.
        # For simplicity, we assume it downloads as mp3.
        audio_file = download_youtube(input_path, output_dir)
    elif input_path.endswith(('.mp4')):
        print("Extracting audio from video...")
        audio_file = extract_audio(input_path, output_dir)
    else:
        audio_file = input_path
        # copy the file to the output directory
        import shutil
        shutil.copy(audio_file, output_dir)
        audio_file = os.path.join(output_dir, os.path.basename(audio_file))


    # Run transcription
    transcripts = []
    for model in models:
        try:
            transcript_file = transcribe(model, audio_file, output_dir)
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
