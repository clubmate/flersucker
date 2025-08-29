"""Parakeet model implementation using the base transcription class."""

import torch
import nemo.collections.asr as nemo_asr
from typing import Any, Dict, List
from .base import BaseTranscriptionModel, create_cli_parser


class ParakeetModel(BaseTranscriptionModel):
    """Parakeet transcription model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.model_name = config.get("model_name", "nvidia/parakeet-tdt-0.6b-v3")
    
    def load_model(self) -> Any:
        """Load the Parakeet model."""
        if self.model is None:
            print(f"Loading Parakeet model: {self.model_name}")
            self.model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(self.model_name)
            self.model = self.model.to(self.device)
            self.model.eval()
        return self.model
    
    def transcribe_audio(self, input_file: str) -> str:
        """Transcribe audio using Parakeet."""
        with torch.no_grad():
            # Use timestamps if available
            transcriptions = self.model.transcribe([input_file], timestamps=True, batch_size=1)
        
        # Extract text from result
        if isinstance(transcriptions, list) and len(transcriptions) > 0:
            hypothesis = transcriptions[0]
            if hasattr(hypothesis, 'text'):
                return hypothesis.text
            else:
                return str(hypothesis)
        else:
            return str(transcriptions)
    
    def format_result(self, text: str, language: str = "de") -> Dict[str, Any]:
        """Format Parakeet result with enhanced segments if available."""
        # For now, use basic format - could be enhanced to extract timestamps
        return super().format_result(text, language)


def transcribe_parakeet(input_file: str, output_file: str, config: Dict[str, Any]) -> None:
    """Transcribe audio file using Parakeet model."""
    model = ParakeetModel(config)
    model.transcribe(input_file, output_file)


if __name__ == "__main__":
    parser = create_cli_parser("Transcribe an audio file using the Parakeet model.")
    args = parser.parse_args()
    
    transcribe_parakeet(args.input_file, args.output_file, args.config)