"""
Example model transcription module for demonstration purposes.
"""
import argparse
import json
import time
from typing import Dict, Any


def transcribe_example(input_file: str, output_file: str, config: Dict[str, Any]):
    """
    A placeholder for example model transcription.
    
    Args:
        input_file: Path to the input audio file
        output_file: Path to the output JSON file
        config: Configuration dictionary (unused in this example)
    """
    print(f"Starting transcription for {input_file} with example model...")
    
    # Simulate processing time
    time.sleep(2)
    
    # Create dummy transcript with proper structure
    transcript = {
        "text": "This is a dummy transcription from the example model.",
        "language": "en",
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "text": "This is a dummy transcription from the example model.",
                "words": [
                    {"start": 0.0, "end": 0.5, "word": "This"},
                    {"start": 0.5, "end": 0.8, "word": "is"},
                    {"start": 0.8, "end": 1.0, "word": "a"},
                    {"start": 1.0, "end": 1.5, "word": "dummy"},
                    {"start": 1.5, "end": 2.5, "word": "transcription"},
                    {"start": 2.5, "end": 2.8, "word": "from"},
                    {"start": 2.8, "end": 3.0, "word": "the"},
                    {"start": 3.0, "end": 3.5, "word": "example"},
                    {"start": 3.5, "end": 4.0, "word": "model."}
                ]
            }
        ]
    }
    
    # Save to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=4, ensure_ascii=False)
    
    print(f"Example transcription saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file using a dummy example model."
    )
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()
    
    transcribe_example(args.input_file, args.output_file, args.config)