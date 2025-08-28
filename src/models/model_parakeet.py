import argparse
import json
import torch
import nemo.collections.asr as nemo_asr
from nemo.core import ModelPT
import os

def transcribe_parakeet(input_file, output_file, config):
    """
    Transcribes an audio file using the Parakeet model from NVIDIA NeMo.
    """
    print(f"Starting transcription for {input_file} with Parakeet...")

    # Get configuration parameters
    model_name = config.get("model_name", "nvidia/parakeet-tdt-0.6b-v3")
    device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")

    try:
        # Load the Parakeet model
        print(f"Loading Parakeet model: {model_name}")
        model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name)
        model = model.to(device)
        model.eval()

        print("Model loaded successfully. Starting transcription...")

        # Perform transcription
        with torch.no_grad():
            # NeMo expects audio files and returns transcription
            transcriptions = model.transcribe([input_file], batch_size=1)

        # Process the result
        if isinstance(transcriptions, list) and len(transcriptions) > 0:
            # Extract text from Hypothesis object
            hypothesis = transcriptions[0]
            if hasattr(hypothesis, 'text'):
                text = hypothesis.text
            else:
                text = str(hypothesis)
        else:
            text = str(transcriptions)

        # Create result structure similar to Whisper
        result = {
            "text": text,
            "language": "de",  # Assuming German based on the project context
            "segments": [
                {
                    "start": 0.0,
                    "end": 0.0,  # NeMo doesn't provide timestamps by default
                    "text": text
                }
            ]
        }

        # Save to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"Parakeet transcription saved to {output_file}")

    except Exception as e:
        print(f"Error during Parakeet transcription: {str(e)}")
        # Fallback to dummy result
        result = {
            "text": f"Error: {str(e)}",
            "language": "unknown",
            "segments": [{"start": 0.0, "end": 0.0, "text": f"Error: {str(e)}"}]
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the Parakeet model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()

    transcribe_parakeet(args.input_file, args.output_file, args.config)