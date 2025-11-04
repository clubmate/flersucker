import argparse
import json
import torch
import stable_whisper
import os
import logging
import gc

def transcribe_stablew(input_file, output_file, config):
    """
    Transcribes an audio file using Stable-ts (Stable Whisper Timestamps).
    Stable-ts improves Whisper's timestamp accuracy and eliminates overlaps.
    Provides highly accurate word-level timestamps without forced alignment.
    """
    # Reduce logging verbosity
    logging.getLogger('stable_whisper').setLevel(logging.ERROR)
    logging.getLogger('whisper').setLevel(logging.ERROR)
    logging.getLogger('transformers').setLevel(logging.ERROR)
    
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    print(f"Starting transcription for {input_file} with Stable-Whisper...")

    # Get configuration parameters
    model_size = config.get("model_size", "large-v3")
    device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    language = config.get("language", "de")
    
    # Note: stable-whisper uses standard Whisper, no compute_type parameter
    # It automatically uses the appropriate dtype based on device
    
    # Stable-ts specific parameters
    vad = config.get("vad", True)  # Voice Activity Detection
    vad_threshold = config.get("vad_threshold", 0.35)
    vad_onnx = config.get("vad_onnx", False)  # Use ONNX for faster VAD
    
    # Timestamp stabilization parameters
    suppress_silence = config.get("suppress_silence", True)
    suppress_word_ts = config.get("suppress_word_ts", True)
    min_word_dur = config.get("min_word_dur", 0.1)  # Minimum word duration
    max_word_dur = config.get("max_word_dur", 3.0)  # Maximum word duration
    nonspeech_error = config.get("nonspeech_error", 0.1)
    
    # Refinement options
    refine = config.get("refine", True)  # Post-process for better timestamps
    only_voice_freq = config.get("only_voice_freq", False)  # Filter non-voice frequencies

    print(f"Loading Stable-Whisper model: {model_size}")
    print(f"Device: {device}")
    
    try:
        # 1. Load Stable-Whisper model (no compute_type parameter)
        model = stable_whisper.load_model(
            model_size,
            device=device
        )
        
        print("Model loaded. Transcribing...")
        
        # 2. Transcribe with stable timestamps
        # Note: Some parameters are only for refine(), not transcribe()
        result = model.transcribe(
            input_file,
            language=language,
            vad=vad,
            vad_threshold=vad_threshold,
            vad_onnx=vad_onnx,
            suppress_silence=suppress_silence,
            suppress_word_ts=suppress_word_ts,
            word_timestamps=True  # Always get word timestamps
        )
        
        print(f"Initial transcription complete.")
        
        # 3. Refine timestamps for maximum accuracy
        if refine:
            print("Refining timestamps for improved accuracy...")
            # refine() uses different parameters - it's primarily for audio realignment
            # The main stabilization already happened in transcribe()
            try:
                result = model.refine(
                    input_file,
                    result
                    # Note: refine() doesn't accept these parameters directly
                    # Stabilization is already done by transcribe() with vad and suppress_* options
                )
                print("Timestamp refinement complete.")
            except Exception as e:
                print(f"Refinement skipped: {e}")
                print("Using transcription results without additional refinement.")
        
        # 4. Convert result to our JSON format (match Parakeet format)
        segments = []
        full_text_parts = []
        
        for segment in result.segments:
            seg_text = segment.text.strip()
            full_text_parts.append(seg_text)
            
            # Extract words with timestamps
            words = []
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    words.append({
                        "word": word.word.strip(),
                        "start": float(word.start),
                        "end": float(word.end),
                        "probability": float(word.probability) if hasattr(word, 'probability') else 1.0
                    })
            
            segments.append({
                "start": float(segment.start),
                "end": float(segment.end),
                "text": seg_text,
                "words": words
            })
        
        # Build complete text
        full_text = " ".join(full_text_parts).strip()
        
        # 5. Prepare final output (match Parakeet format exactly)
        transcript = {
            "text": full_text,
            "language": result.language if hasattr(result, 'language') else language,
            "segments": segments
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        print(f"Stable-Whisper transcription saved to {output_file}")
        print(f"Total segments: {len(segments)}")
        
        # Validate no overlaps
        overlaps = 0
        for i in range(len(segments) - 1):
            if segments[i]['end'] > segments[i+1]['start']:
                overlaps += 1
        
        if overlaps == 0:
            print("✅ No timestamp overlaps detected!")
        else:
            print(f"⚠️  Warning: {overlaps} timestamp overlaps found (this should not happen with stable-ts)")
        
        # Clean up
        del model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"Error during Stable-Whisper transcription: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Stable-Whisper.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", required=True, help="JSON string with model configuration.")
    args = parser.parse_args()
    
    # Parse config JSON
    config = json.loads(args.config)
    
    transcribe_stablew(args.input_file, args.output_file, config)
