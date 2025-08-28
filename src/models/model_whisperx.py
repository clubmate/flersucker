import argparse
import json
import whisperx
import torch

def transcribe_whisperx(input_file, output_file, config):
    """
    Transcribes an audio file using the whisperx model.
    """
    print(f"Starting transcription for {input_file} with whisperx...")
    
    device = config.get("device", "cuda")
    if device == "cuda" and not torch.cuda.is_available():
        print("Warning: CUDA not available, falling back to CPU for whisperx model.")
        device = "cpu"
        
    model_size = config.get("model_size", "large-v3")
    batch_size = config.get("batch_size", 16)
    compute_type = config.get("compute_type", "float16")
    if device == "cpu":
        compute_type = "int8"

    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model(model_size, device, compute_type=compute_type)

    audio = whisperx.load_audio(input_file)
    print("Transcribing audio...")
    result = model.transcribe(audio, batch_size=batch_size)

    print("Aligning transcription...")
    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
        
    print(f"WhisperX transcription saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the whisperx model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()
    
    transcribe_whisperx(args.input_file, args.output_file, args.config)
