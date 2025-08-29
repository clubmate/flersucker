"""Base class for transcription models to eliminate code duplication."""

import argparse
import json
import torch
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class BaseTranscriptionModel(ABC):
    """Abstract base class for all transcription models."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the model with configuration."""
        self.config = config
        self.device = self._get_device()
        
    def _get_device(self) -> str:
        """Determine the best available device."""
        device = self.config.get("device", "cuda")
        if device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU.")
            return "cpu"
        return device
    
    @abstractmethod
    def load_model(self) -> Any:
        """Load the specific model. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def transcribe_audio(self, input_file: str) -> str:
        """Transcribe audio file and return raw transcription text."""
        pass
    
    def format_result(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Format transcription result into standard structure."""
        return {
            "text": text,
            "language": language,
            "segments": [{
                "start": 0.0,
                "end": 0.0,
                "text": text
            }]
        }
    
    def save_result(self, result: Dict[str, Any], output_file: str) -> None:
        """Save transcription result to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    
    def transcribe(self, input_file: str, output_file: str) -> None:
        """Complete transcription workflow."""
        print(f"Starting transcription for {input_file} with {self.__class__.__name__}...")
        
        try:
            self.load_model()
            text = self.transcribe_audio(input_file)
            result = self.format_result(text)
            self.save_result(result, output_file)
            print(f"Transcription saved to {output_file}")
            
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            # Save error result
            error_result = self.format_result(f"Error: {str(e)}", "unknown")
            self.save_result(error_result, output_file)


def create_cli_parser(description: str) -> argparse.ArgumentParser:
    """Create standard argument parser for model scripts."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input_file", required=True, 
                       help="Path to the input audio file.")
    parser.add_argument("--output_file", required=True, 
                       help="Path to the output JSON file.")
    parser.add_argument("--config", type=json.loads, default={}, 
                       help="JSON string with model configurations.")
    return parser