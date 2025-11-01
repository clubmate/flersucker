import argparse
import json
import torch
import whisperx
import os
import logging
import gc

def transcribe_whisperx(input_file, output_file, config):
    """
    Transcribes an audio file using WhisperX with word-level timestamps.
    WhisperX provides enhanced Whisper with accurate word-level timestamps
    using phonetic forced alignment.
    """
    # Reduce logging verbosity
    logging.getLogger('whisperx').setLevel(logging.ERROR)
    logging.getLogger('faster_whisper').setLevel(logging.ERROR)
    logging.getLogger('transformers').setLevel(logging.ERROR)
    
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    print(f"Starting transcription for {input_file} with WhisperX...")

    # Get configuration parameters
    model_size = config.get("model_size", "large-v3")
    device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    compute_type = config.get("compute_type", "float16" if device == "cuda" else "int8")
    batch_size = config.get("batch_size", 16)
    language = config.get("language", "de")  # German by default
    
    # Alignment and diarization settings
    enable_alignment = config.get("enable_alignment", True)
    enable_diarization = config.get("enable_diarization", False)
    hf_token = config.get("hf_token", None)  # Hugging Face token for diarization
    min_speakers = config.get("min_speakers", None)
    max_speakers = config.get("max_speakers", None)

    print(f"Loading WhisperX model: {model_size}")
    print(f"Device: {device}, Compute type: {compute_type}")
    
    try:
        # 1. Load WhisperX model
        model = whisperx.load_model(
            model_size, 
            device, 
            compute_type=compute_type,
            language=language
        )
        
        print("Model loaded. Transcribing...")
        
        # 2. Transcribe with Whisper
        audio = whisperx.load_audio(input_file)
        result = model.transcribe(audio, batch_size=batch_size, language=language)
        
        # Get initial transcript
        segments = result.get("segments", [])
        
        # Build full text from all segments (like Parakeet does)
        full_text = " ".join([seg.get("text", "").strip() for seg in segments]).strip()
        
        print(f"Initial transcription complete. {len(segments)} segments found.")
        
        # 3. Align whisper output for word-level timestamps
        word_segments = []
        if enable_alignment and segments:
            print("Performing word-level alignment...")
            
            # Load alignment model
            model_a, metadata = whisperx.load_align_model(
                language_code=result["language"], 
                device=device
            )
            
            # Align
            result_aligned = whisperx.align(
                result["segments"], 
                model_a, 
                metadata, 
                audio, 
                device,
                return_char_alignments=False
            )
            
            # Extract word-level timestamps from aligned result
            for segment in result_aligned["segments"]:
                seg_start = segment.get("start", 0.0)
                seg_end = segment.get("end", 0.0)
                seg_text = segment.get("text", "")
                
                # Extract words with timestamps
                words = []
                if "words" in segment:
                    for word_info in segment["words"]:
                        words.append({
                            "word": word_info.get("word", ""),
                            "start": word_info.get("start", seg_start),
                            "end": word_info.get("end", seg_end),
                            "score": word_info.get("score", 1.0)
                        })
                
                word_segments.append({
                    "start": seg_start,
                    "end": seg_end,
                    "text": seg_text,
                    "words": words
                })
            
            print(f"Alignment complete. Word-level timestamps added.")
            
            # Clean up alignment model
            del model_a
            gc.collect()
            if device == "cuda":
                torch.cuda.empty_cache()
        else:
            # No alignment - use segment-level timestamps only
            for segment in segments:
                word_segments.append({
                    "start": segment.get("start", 0.0),
                    "end": segment.get("end", 0.0),
                    "text": segment.get("text", ""),
                    "words": []  # No word-level timestamps
                })
        
        # 4. Optional: Speaker Diarization
        if enable_diarization and hf_token:
            print("Performing speaker diarization...")
            
            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=hf_token, 
                device=device
            )
            
            diarize_segments = diarize_model(
                audio,
                min_speakers=min_speakers,
                max_speakers=max_speakers
            )
            
            # Assign speakers to segments
            result_diarized = whisperx.assign_word_speakers(
                diarize_segments, 
                result_aligned if enable_alignment else result
            )
            
            # Update segments with speaker information
            for i, segment in enumerate(result_diarized["segments"]):
                if i < len(word_segments):
                    word_segments[i]["speaker"] = segment.get("speaker", "UNKNOWN")
            
            print("Diarization complete.")
            
            # Clean up diarization model
            del diarize_model
            gc.collect()
            if device == "cuda":
                torch.cuda.empty_cache()
        
        # 5. Prepare final output (match Parakeet format)
        transcript = {
            "text": full_text,  # Complete transcript text
            "language": result.get("language", language),
            "segments": word_segments
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        print(f"WhisperX transcription saved to {output_file}")
        
        # Clean up
        del model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"Error during WhisperX transcription: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using WhisperX.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", required=True, help="JSON string with model configuration.")
    args = parser.parse_args()
    
    # Parse config JSON
    config = json.loads(args.config)
    
    transcribe_whisperx(args.input_file, args.output_file, config)
