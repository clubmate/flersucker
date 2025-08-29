"""Whisper model implementation using the base transcription class."""

import whisper
from typing import Any, Dict
from .base import BaseTranscriptionModel, create_cli_parser


class WhisperModel(BaseTranscriptionModel):
    """Whisper transcription model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.model_size = config.get("model_size", "large-v3")
    
    def load_model(self) -> Any:
        """Load the Whisper model."""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
        return self.model
    
    def transcribe_audio(self, input_file: str) -> str:
        """Transcribe audio using Whisper and return the result."""
        result = self.model.transcribe(input_file, verbose=True)
        return result
    
    def format_result(self, result: Dict[str, Any], language: str = "auto") -> Dict[str, Any]:
        """Format Whisper result (already in correct format)."""
        return result


def transcribe_whisper(input_file: str, output_file: str, config: Dict[str, Any]) -> None:
    """Transcribe audio file using Whisper model."""
    model = WhisperModel(config)
    model.transcribe(input_file, output_file)


if __name__ == "__main__":
    parser = create_cli_parser("Transcribe an audio file using the Whisper model.")
    args = parser.parse_args()
    
    transcribe_whisper(args.input_file, args.output_file, args.config)
