import argparse
import json
import nemo.collections.asr as nemo_asr
import torch
import os

def transcribe_parakeet(input_file, output_file, config):
    """
    Transcribes an audio file using the Parakeet model from NVIDIA NeMo.
    """
    print(f"Starting transcription for {input_file} with Parakeet...")

    model_name = config.get("model_size", "nvidia/parakeet-tdt-0.6b-v3")
    device = config.get("device", "cuda")
    if device == "cuda" and not torch.cuda.is_available():
        print("Warning: CUDA not available, falling back to CPU for Parakeet model.")
        device = "cpu"

    # Suppress a specific warning from omegaconf
    from omegaconf import OmegaConf
    OmegaConf.set_struct(True, False)

    asr_model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name)
    
    # Set up the decoding config for timestamp prediction
    from omegaconf import open_dict
    with open_dict(asr_model.cfg.decoding):
        asr_model.cfg.decoding.compute_timestamps = True
        asr_model.cfg.decoding.ctc_timestamp_type = "word" # can be "char" or "word"

    asr_model.to(device)

    # Run transcription and get word timestamps
    hypotheses = asr_model.transcribe(paths2audio_files=[input_file], return_hypotheses=True)

    if not hypotheses or not hypotheses[0].word_alignments:
        print("Could not generate timestamps for Parakeet.")
        # Fallback to transcription without timestamps
        text = asr_model.transcribe(paths2audio_files=[input_file])[0]
        result = {"text": text, "segments": [{"text": text, "start": 0, "end": -1}]}
    else:
        # Group words into segments (sentences)
        segments = []
        current_segment = None
        
        for word_alignment in hypotheses[0].word_alignments:
            word = word_alignment.word
            start_time = word_alignment.start_offset
            end_time = word_alignment.end_offset

            if current_segment is None:
                current_segment = {"text": word, "start": start_time, "end": end_time}
            else:
                current_segment["text"] += " " + word
                current_segment["end"] = end_time

            # End segment on punctuation
            if word.endswith(('.', '?', '!')):
                segments.append(current_segment)
                current_segment = None
        
        # Add the last segment if it exists
        if current_segment is not None:
            segments.append(current_segment)

        full_text = " ".join([seg["text"] for seg in segments])
        result = {"text": full_text, "segments": segments}


    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
        
    print(f"Parakeet transcription saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the Parakeet model.")
    parser.add_argument("--input_file", required=True, help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, help="JSON string with model configurations.")
    args = parser.parse_args()
    
    transcribe_parakeet(args.input_file, args.output_file, args.config)
