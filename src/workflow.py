"""Main workflow orchestrator for the transcription tool."""

from pathlib import Path
from typing import List
import sys

from .config import ConfigManager
from .download import download_youtube, extract_audio, DownloadError, AudioExtractionError
from .transcribe import transcribe, TranscriptionError
from .consensus import create_consensus
from .utils import (
    is_youtube_url, is_video_file, is_audio_file, 
    create_output_directory, copy_file_to_directory
)


class TranscriptionWorkflow:
    """Orchestrates the complete transcription workflow."""
    
    def __init__(self, config_manager: ConfigManager, verbose: bool = False):
        """Initialize the workflow."""
        self.config = config_manager
        self.verbose = verbose
    
    def run(self, input_path: str, models: List[str], output_base_dir: str = "output",
            create_consensus_flag: bool = True) -> None:
        """Run the complete transcription workflow."""
        try:
            # Get models to use
            selected_models = self.config.get_models(models)
            if not selected_models:
                print("No models selected. Exiting.")
                return
            
            print(f"Using models: {', '.join(selected_models)}")
            
            # Create output directory
            output_dir = create_output_directory(input_path, output_base_dir)
            print(f"Output will be saved in: {output_dir}")
            
            # Prepare audio file
            audio_file = self._prepare_audio_file(input_path, output_dir)
            print(f"Audio file ready: {audio_file.name}")
            
            # Run transcriptions
            transcript_files = self._run_transcriptions(selected_models, audio_file, output_dir)
            
            # Create consensus if requested and multiple transcripts exist
            if create_consensus_flag and len(transcript_files) > 1:
                self._create_consensus(transcript_files, output_dir)
            
            print(f"\nTranscription complete! Results saved in: {output_dir}")
            
        except Exception as e:
            print(f"Workflow failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    def _prepare_audio_file(self, input_path: str, output_dir: Path) -> Path:
        """Prepare audio file from various input sources."""
        if is_youtube_url(input_path):
            return self._handle_youtube_input(input_path, output_dir)
        elif is_video_file(input_path):
            return self._handle_video_input(input_path, output_dir)
        elif is_audio_file(input_path):
            return self._handle_audio_input(input_path, output_dir)
        else:
            # Assume it's an audio file and try to copy it
            print(f"Unknown file type for {input_path}, treating as audio file...")
            return copy_file_to_directory(input_path, output_dir)
    
    def _handle_youtube_input(self, url: str, output_dir: Path) -> Path:
        """Handle YouTube URL input."""
        print("Downloading from YouTube...")
        try:
            video_quality = self.config.get_video_quality()
            video_path = download_youtube(url, output_dir, video_quality)
            
            print("Extracting audio from video...")
            audio_config = self.config.get_audio_config()
            return extract_audio(video_path, output_dir, audio_config)
            
        except DownloadError as e:
            raise Exception(f"YouTube download failed: {e}")
        except AudioExtractionError as e:
            raise Exception(f"Audio extraction failed: {e}")
    
    def _handle_video_input(self, video_path: str, output_dir: Path) -> Path:
        """Handle local video file input."""
        print("Extracting audio from video...")
        try:
            # Copy video file to output directory
            copied_video = copy_file_to_directory(video_path, output_dir)
            
            # Extract audio
            audio_config = self.config.get_audio_config()
            return extract_audio(copied_video, output_dir, audio_config)
            
        except AudioExtractionError as e:
            raise Exception(f"Audio extraction failed: {e}")
    
    def _handle_audio_input(self, audio_path: str, output_dir: Path) -> Path:
        """Handle local audio file input."""
        print("Using audio file directly...")
        return copy_file_to_directory(audio_path, output_dir)
    
    def _run_transcriptions(self, models: List[str], audio_file: Path, 
                          output_dir: Path) -> List[str]:
        """Run transcriptions with all selected models."""
        transcript_files = []
        
        for model in models:
            try:
                print(f"\n--- Running {model} transcription ---")
                model_config = self.config.get_model_config(model)
                transcript_file = transcribe(model, audio_file, output_dir, model_config)
                transcript_files.append(str(transcript_file))
                print(f"✓ {model} transcription complete")
                
            except TranscriptionError as e:
                print(f"✗ {model} transcription failed: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
            except Exception as e:
                print(f"✗ Unexpected error during {model} transcription: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
        
        if not transcript_files:
            raise Exception("All transcriptions failed!")
        
        return transcript_files
    
    def _create_consensus(self, transcript_files: List[str], output_dir: Path) -> None:
        """Create consensus transcription."""
        print(f"\n--- Creating consensus transcription ---")
        try:
            consensus_output = output_dir / "consensus.json"
            create_consensus(transcript_files, str(consensus_output))
            print("✓ Consensus transcription complete")
        except Exception as e:
            print(f"✗ Consensus creation failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()