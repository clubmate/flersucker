import argparse
import json
import whisper
import torch

def transcribe_whisper(input_file, output_file, config):
    """
    Transcribes an audio file using the whisper model.
    """
    print(f"Starting transcription for {input_file} with whisper...")
    
    model_size = config.get("model_size", "large-v3")
    device = config.get("device", "cuda")
    if device == "cuda" and not torch.cuda.is_available():
        print("Warning: CUDA not available, falling back to CPU for whisper model.")
        device = "cpu"

    model = whisper.load_model(model_size, device=device)
    result = model.transcribe(input_file, verbose=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
        
    print(f"Whisper transcription saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the whisper model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()
    
    transcribe_whisper(args.input_file, args.output_file, args.config)
