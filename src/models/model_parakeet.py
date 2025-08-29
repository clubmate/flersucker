"""
Parakeet model transcription module using NVIDIA NeMo.
"""
import argparse
import json
import os
import sys
import logging
import warnings
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List

import torch
import nemo.collections.asr as nemo_asr


def configure_logging():
    """Configure logging to reduce verbosity during model operations."""
    loggers = ['nemo', 'nemo_logger', 'pytorch_lightning', 'transformers', 'huggingface_hub']
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)
    
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)


def transcribe_parakeet(input_file: str, output_file: str, config: Dict[str, Any]):
    """
    Transcribe an audio file using the Parakeet model from NVIDIA NeMo.
    
    Args:
        input_file: Path to the input audio file
        output_file: Path to the output JSON file
        config: Configuration dictionary with model parameters
    """
    configure_logging()
    
    print(f"Starting transcription for {input_file} with Parakeet...")
    
    # Get configuration parameters
    model_name = config.get("model_name", "nvidia/parakeet-tdt-0.6b-v3")
    device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    
    try:
        result = _perform_transcription(input_file, model_name, device)
        _save_result(result, output_file)
        print(f"Parakeet transcription saved to {output_file}")
        
    except Exception as e:
        print(f"Error during Parakeet transcription: {str(e)}")
        result = _create_error_result(str(e))
        _save_result(result, output_file)


def _perform_transcription(input_file: str, model_name: str, device: str) -> Dict[str, Any]:
    """Perform the actual transcription with the model."""
    print("Loading Parakeet model...")
    
    # Load model with suppressed output
    with redirect_stdout(open(os.devnull, 'w')), redirect_stderr(open(os.devnull, 'w')):
        model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name)
        model = model.to(device)
        model.eval()
    
    print("Model loaded. Transcribing...")
    
    # Perform transcription with timestamps
    with torch.no_grad():
        with redirect_stdout(open(os.devnull, 'w')):
            transcriptions = model.transcribe([input_file], timestamps=True, batch_size=1)
    
    return _process_transcription_result(transcriptions)


def _process_transcription_result(transcriptions: List) -> Dict[str, Any]:
    """Process the raw transcription result into structured format."""
    if not isinstance(transcriptions, list) or len(transcriptions) == 0:
        return _create_error_result("No transcription result returned")
    
    hypothesis = transcriptions[0]
    
    # Extract text
    text = hypothesis.text if hasattr(hypothesis, 'text') else str(hypothesis)
    
    # Extract segments with timestamps
    segments = _extract_segments(hypothesis, text)
    
    return {
        "text": text,
        "language": "auto",  # Parakeet supports multiple languages
        "segments": segments
    }


def _extract_segments(hypothesis, fallback_text: str) -> List[Dict[str, Any]]:
    """Extract segments with word-level timestamps from hypothesis."""
    segments = []
    
    if hasattr(hypothesis, 'timestamp') and 'segment' in hypothesis.timestamp:
        for seg in hypothesis.timestamp['segment']:
            segment_data = {
                "start": float(seg['start']),
                "end": float(seg['end']),
                "text": seg['segment'],
                "words": _extract_words_for_segment(hypothesis, seg)
            }
            segments.append(segment_data)
    else:
        # Fallback if no timestamps available
        segments = [{
            "start": 0.0,
            "end": 0.0,
            "text": fallback_text,
            "words": []
        }]
    
    return segments


def _extract_words_for_segment(hypothesis, segment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract word-level timestamps for a segment."""
    words = []
    
    if hasattr(hypothesis, 'timestamp') and 'word' in hypothesis.timestamp:
        segment_start = float(segment['start'])
        segment_end = float(segment['end'])
        
        for word in hypothesis.timestamp['word']:
            word_start = float(word['start'])
            word_end = float(word['end'])
            
            # Check if word falls within this segment's time range
            if segment_start <= word_start <= segment_end:
                words.append({
                    "start": word_start,
                    "end": word_end,
                    "word": word['word']
                })
    
    return words


def _create_error_result(error_message: str) -> Dict[str, Any]:
    """Create an error result structure."""
    return {
        "text": f"Error: {error_message}",
        "language": "unknown",
        "segments": [{
            "start": 0.0,
            "end": 0.0,
            "text": f"Error: {error_message}",
            "words": []
        }]
    }


def _save_result(result: Dict[str, Any], output_file: str):
    """Save the result to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the Parakeet model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()
    
    transcribe_parakeet(args.input_file, args.output_file, args.config)