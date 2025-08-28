import argparse
import json
from faster_whisper import WhisperModel
import torch

def transcribe_faster_whisper(input_file, output_file, config):
    """
    Transcribes an audio file using the faster-whisper model.
    """
    print(f"Starting transcription for {input_file} with faster-whisper...")
    
    model_size = config.get("model_size", "large-v3")
    device = config.get("device", "cuda")
    if device == "cuda" and not torch.cuda.is_available():
        print("Warning: CUDA not available, falling back to CPU for faster-whisper model.")
        device = "cpu"
        
    compute_type = config.get("compute_type", "float16")
    if device == "cpu":
        compute_type = "int8"

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(input_file, beam_size=5, vad_filter=True)

    result = {
        "language": info.language,
        "language_probability": info.language_probability,
        "segments": []
    }

    for segment in segments:
        result["segments"].append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
        
    print(f"Faster Whisper transcription saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the faster-whisper model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()
    
    transcribe_faster_whisper(args.input_file, args.output_file, args.config)
