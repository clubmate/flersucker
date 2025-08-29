"""Enhanced consensus creation for multiple transcriptions."""

import json
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import difflib


def load_transcription(file_path: str) -> Dict[str, Any]:
    """Load transcription from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_text(transcription: Dict[str, Any]) -> str:
    """Extract text from transcription result."""
    return transcription.get('text', '').strip()


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings."""
    matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
    return matcher.ratio()


def find_best_transcription(transcriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find the best transcription based on agreement with others."""
    if len(transcriptions) == 1:
        return transcriptions[0]
    
    texts = [extract_text(t) for t in transcriptions]
    similarity_scores = []
    
    # Calculate average similarity for each transcription
    for i, text in enumerate(texts):
        similarities = []
        for j, other_text in enumerate(texts):
            if i != j:
                similarities.append(calculate_similarity(text, other_text))
        similarity_scores.append(sum(similarities) / len(similarities) if similarities else 0)
    
    # Return transcription with highest average similarity
    best_index = similarity_scores.index(max(similarity_scores))
    return transcriptions[best_index]


def create_word_level_consensus(transcriptions: List[Dict[str, Any]]) -> str:
    """Create consensus by voting on individual words."""
    if not transcriptions:
        return ""
    
    if len(transcriptions) == 1:
        return extract_text(transcriptions[0])
    
    # Split all texts into words
    all_words = []
    for transcription in transcriptions:
        text = extract_text(transcription)
        words = text.split()
        all_words.append(words)
    
    if not all_words:
        return ""
    
    # Find the longest transcription as reference
    max_length = max(len(words) for words in all_words)
    consensus_words = []
    
    # For each position, vote on the most common word
    for pos in range(max_length):
        candidates = []
        for words in all_words:
            if pos < len(words):
                candidates.append(words[pos].lower())
        
        if candidates:
            # Use most common word (simple majority vote)
            word_counts = Counter(candidates)
            most_common_word = word_counts.most_common(1)[0][0]
            consensus_words.append(most_common_word)
    
    return " ".join(consensus_words)


def create_consensus(transcript_files: List[str], output_file: str) -> None:
    """Create a consensus transcription from multiple sources."""
    if not transcript_files:
        print("No transcription files provided for consensus.")
        return
    
    print(f"Creating consensus from {len(transcript_files)} transcriptions...")
    
    # Load all transcriptions
    transcriptions = []
    for file_path in transcript_files:
        try:
            transcription = load_transcription(file_path)
            transcriptions.append(transcription)
            print(f"Loaded: {Path(file_path).name}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if not transcriptions:
        print("No valid transcriptions found.")
        return
    
    if len(transcriptions) == 1:
        # Just copy the single transcription
        consensus_text = extract_text(transcriptions[0])
        best_transcription = transcriptions[0]
    else:
        # Create consensus using word-level voting
        consensus_text = create_word_level_consensus(transcriptions)
        
        # Find best overall transcription for metadata
        best_transcription = find_best_transcription(transcriptions)
    
    # Create consensus result
    consensus_result = {
        "text": consensus_text,
        "language": best_transcription.get("language", "auto"),
        "segments": [{
            "start": 0.0,
            "end": 0.0,
            "text": consensus_text
        }],
        "consensus_info": {
            "source_count": len(transcriptions),
            "source_files": [Path(f).name for f in transcript_files],
            "method": "word_level_voting" if len(transcriptions) > 1 else "single_source"
        }
    }
    
    # Save consensus result
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(consensus_result, f, indent=4, ensure_ascii=False)
    
    print(f"Consensus transcript saved to {output_file}")
    print(f"Consensus method: {consensus_result['consensus_info']['method']}")
    print(f"Final text length: {len(consensus_text)} characters")
