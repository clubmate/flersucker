"""Canary model implementation using the base transcription class."""

import torch
import nemo.collections.asr as nemo_asr
from typing import Any, Dict
from .base import BaseTranscriptionModel, create_cli_parser


class CanaryModel(BaseTranscriptionModel):
    """Canary transcription model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.model_name = config.get("model_name", "nvidia/canary-1b")
    
    def load_model(self) -> Any:
        """Load the Canary model."""
        if self.model is None:
            print(f"Loading Canary model: {self.model_name}")
            self.model = nemo_asr.models.EncDecMultiTaskModel.from_pretrained(self.model_name)
            self.model = self.model.to(self.device)
            self.model.eval()
        return self.model
    
    def transcribe_audio(self, input_file: str) -> str:
        """Transcribe audio using Canary."""
        with torch.no_grad():
            transcriptions = self.model.transcribe([input_file], batch_size=1)
        
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
        """Format Canary result with German as default language."""
        return super().format_result(text, language)


def transcribe_canary(input_file: str, output_file: str, config: Dict[str, Any]) -> None:
    """Transcribe audio file using Canary model."""
    model = CanaryModel(config)
    model.transcribe(input_file, output_file)


if __name__ == "__main__":
    parser = create_cli_parser("Transcribe an audio file using the Canary model.")
    args = parser.parse_args()
    
    transcribe_canary(args.input_file, args.output_file, args.config)