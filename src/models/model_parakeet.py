import argparse
import json
import torch
import nemo.collections.asr as nemo_asr
from nemo.core import ModelPT
import os
import logging

def transcribe_parakeet(input_file, output_file, config):
    """
    Transcribes an audio file using the Parakeet model from NVIDIA NeMo.
    Returns both segment-level and word-level timestamps.
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

    print(f"Starting transcription for {input_file} with Parakeet...")

    # Get configuration parameters
    model_name = config.get("model_name", "nvidia/parakeet-tdt-0.6b-v3")
    device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")

    try:
        # Load the Parakeet model (reduced output)
        print(f"Loading Parakeet model...")
        
        # Suppress stdout temporarily during model loading
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        with redirect_stdout(open(os.devnull, 'w')), redirect_stderr(open(os.devnull, 'w')):
            model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name)
            model = model.to(device)
            model.eval()
            
            # Check for multi-GPU support
            use_multigpu = config.get("use_multigpu", False)
            if use_multigpu and torch.cuda.device_count() > 1 and device.startswith("cuda"):
                print(f"🚀 Enabling DataParallel on {torch.cuda.device_count()} GPUs")
                model = torch.nn.DataParallel(model)
            else:
                print(f"Using single GPU/CPU: {device}")
            
            # Apply memory optimizations for long audio files
            # Based on https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2/discussions/15
            
            # Get memory optimization settings from config
            enable_local_attention = config.get("enable_local_attention", True)
            local_attention_window = config.get("local_attention_window", [128, 128])
            enable_chunking = config.get("enable_chunking", True)
            
            if enable_local_attention:
                # Enable local attention to reduce memory usage
                # This limits the attention window to reduce VRAM usage
                print(f"Enabling local attention with window {local_attention_window}")
                model.change_attention_model("rel_pos_local_attn", local_attention_window)
            
            if enable_chunking:
                # Enable chunking for subsampling module to further reduce memory usage
                print("Enabling chunked subsampling")
                model.change_subsampling_conv_chunking_factor(1)  # 1 = auto select
        
        print("Model loaded. Transcribing...")

        # Perform transcription with timestamps
        with torch.no_grad():
            # Clear GPU cache before transcription
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # NeMo expects audio files and returns transcription with timestamps
            # This includes both segment and word-level timestamps
            # Use smaller batch size to reduce memory usage
            batch_size = config.get("batch_size", 1)
            
            with redirect_stdout(open(os.devnull, 'w')):  # Only suppress stdout, keep stderr for tqdm
                transcriptions = model.transcribe([input_file], timestamps=True, batch_size=batch_size)

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
            "language": "de",  # Assuming German based on the project context
            "segments": segments
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
            "segments": [{"start": 0.0, "end": 0.0, "text": f"Error: {str(e)}", "words": []}]
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