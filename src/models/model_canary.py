import argparse
import json
import torch
import nemo.collections.asr as nemo_asr
from nemo.core import ModelPT
import os
import logging

def transcribe_canary(input_file, output_file, config):
    """
    Transcribes an audio file using the NVIDIA Canary-1B-v2 model.
    Supports multilingual ASR and translation, optimized for German content.
    """
    # Reduce NeMo logging verbosity - suppress all warnings and info
    logging.getLogger('nemo').setLevel(logging.ERROR)
    logging.getLogger('nemo_logger').setLevel(logging.ERROR)
    logging.getLogger('pytorch_lightning').setLevel(logging.ERROR)
    logging.getLogger('transformers').setLevel(logging.ERROR)
    logging.getLogger('huggingface_hub').setLevel(logging.ERROR)

    # Also suppress warnings module
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    print(f"Starting transcription for {input_file} with Canary-1B-v2...")

    # Get configuration parameters
    model_name = config.get("model_name", "nvidia/canary-1b-v2")
    device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    source_lang = config.get("source_lang", "de")  # Default to German
    target_lang = config.get("target_lang", "de")  # Default to German (ASR mode)
    enable_timestamps = config.get("timestamps", True)

    try:
        # Load the Canary model
        print(f"Loading Canary model...")
        from nemo.collections.asr.models import ASRModel

        # Suppress stdout temporarily during model loading
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        with redirect_stdout(open(os.devnull, 'w')), redirect_stderr(open(os.devnull, 'w')):
            model = ASRModel.from_pretrained(model_name)
            model = model.to(device)
            model.eval()
            
            # Check for multi-GPU support
            use_multigpu = config.get("use_multigpu", False)
            if use_multigpu and torch.cuda.device_count() > 1 and device.startswith("cuda"):
                print(f"🚀 Enabling DataParallel on {torch.cuda.device_count()} GPUs")
                model = torch.nn.DataParallel(model)
            else:
                print(f"Using single GPU/CPU: {device}")

        print("Model loaded. Transcribing...")

        # Perform transcription with timestamps
        with torch.no_grad():
            # Clear GPU cache before transcription
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Use smaller batch size to reduce memory usage
            batch_size = config.get("batch_size", 1)

            with redirect_stdout(open(os.devnull, 'w')):  # Only suppress stdout, keep stderr for tqdm
                # Canary uses source_lang and target_lang parameters
                # For ASR, source_lang and target_lang should be the same
                # Enable detailed timestamps including word-level
                transcriptions = model.transcribe(
                    [input_file],
                    source_lang=source_lang,
                    target_lang=target_lang,
                    timestamps=True,  # Enable timestamps (includes word-level if available)
                    batch_size=batch_size
                )

        # Process the result
        if isinstance(transcriptions, list) and len(transcriptions) > 0:
            hypothesis = transcriptions[0]

            # Extract text from Hypothesis object
            if hasattr(hypothesis, 'text'):
                text = hypothesis.text
            else:
                text = str(hypothesis)

            # Extract timestamps from the hypothesis
            segments = []
            if hasattr(hypothesis, 'timestamp') and 'segment' in hypothesis.timestamp:
                print(f"Debug: Found {len(hypothesis.timestamp['segment'])} segments")
                if 'word' in hypothesis.timestamp:
                    print(f"Debug: Found {len(hypothesis.timestamp['word'])} words")
                else:
                    print("Debug: No word-level timestamps found")
                
                for seg in hypothesis.timestamp['segment']:
                    segment_data = {
                        "start": float(seg['start']),
                        "end": float(seg['end']),
                        "text": seg['segment'],
                        "words": []
                    }

                    # Extract word-level timestamps if available
                    if 'word' in hypothesis.timestamp:
                        # Find words that belong to this segment
                        for word in hypothesis.timestamp['word']:
                            word_start = float(word['start'])
                            word_end = float(word['end'])

                            # Check if word falls within this segment's time range
                            if word_start >= segment_data['start'] and word_end <= segment_data['end']:
                                segment_data['words'].append({
                                    "start": word_start,
                                    "end": word_end,
                                    "word": word['word']
                                })

                    segments.append(segment_data)
            else:
                print("Debug: No segment timestamps found")
                # Fallback if no timestamps available
                segments = [{
                    "start": 0.0,
                    "end": 0.0,
                    "text": text,
                    "words": []
                }]
        else:
            text = str(transcriptions)
            segments = [{"start": 0.0, "end": 0.0, "text": text, "words": []}]

        # Create result structure with both segment and word-level timestamps
        result = {
            "text": text,
            "language": source_lang,  # Use the configured source language
            "segments": segments
        }

        # Save to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"Canary transcription saved to {output_file}")

    except Exception as e:
        print(f"Error during Canary transcription: {str(e)}")
        # Fallback to dummy result
        result = {
            "text": f"Error: {str(e)}",
            "language": source_lang,
            "segments": [{"start": 0.0, "end": 0.0, "text": f"Error: {str(e)}", "words": []}]
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the NVIDIA Canary-1B-v2 model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()

    transcribe_canary(args.input_file, args.output_file, args.config)