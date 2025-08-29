"""
Transcription processor module for handling end-to-end transcription workflow.
"""
import os
import json
import shutil
from collections import OrderedDict
from typing import Dict, List, Optional, Any

from .download import download_youtube, extract_audio
from .transcribe import transcribe
from .utils import create_output_directory


class TranscriptionProcessor:
    """Handles the complete transcription workflow for a single input."""
    
    def __init__(self, models: List[str], model_configs: Dict[str, Any], 
                 video_quality: str = "best[ext=mp4]/best", 
                 audio_config: Optional[Dict[str, Any]] = None):
        self.models = models
        self.model_configs = model_configs
        self.video_quality = video_quality
        self.audio_config = audio_config or {}
    
    def process(self, input_path: str, metadata_override: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Process a single input (local file or URL) and return list of transcript files.
        
        Args:
            input_path: Path to local file or YouTube URL
            metadata_override: Optional metadata to use instead of extracting
            
        Returns:
            List of paths to generated transcript files
        """
        output_dir = create_output_directory(input_path)
        metadata = metadata_override or {}
        
        # Handle different input types
        audio_path = self._prepare_audio(input_path, output_dir, metadata)
        
        # Set default metadata for local files
        if not metadata:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            metadata = {
                'title': base_name,
                'description': '',
                'uploader': '',
                'upload_date': '',
                'id': ''
            }
        
        # Generate transcripts for each model
        transcript_files = []
        for model in self.models:
            try:
                transcript_file = self._transcribe_with_model(
                    model, audio_path, output_dir, metadata
                )
                transcript_files.append(transcript_file)
            except Exception as e:
                print(f"Model {model} error: {e}")
        
        return transcript_files
    
    def _prepare_audio(self, input_path: str, output_dir: str, metadata: Dict[str, Any]) -> str:
        """Prepare audio file from input (download/copy/extract as needed)."""
        video_path = None
        
        if self._is_youtube_url(input_path):
            print(f"Download: {input_path}")
            video_path, dl_metadata = download_youtube(
                input_path, output_dir, quality=self.video_quality
            )
            # Merge downloaded metadata with existing metadata
            for key, value in dl_metadata.items():
                if key not in metadata or not metadata.get(key):
                    metadata[key] = value
        
        elif input_path.endswith('.mp4'):
            # Copy video file to output directory
            shutil.copy(input_path, output_dir)
            video_path = os.path.join(output_dir, os.path.basename(input_path))
        
        # Extract or copy audio
        if video_path:
            audio_name = os.path.splitext(os.path.basename(video_path))[0] + '.wav'
            audio_path = os.path.join(output_dir, audio_name)
            
            if os.path.exists(audio_path):
                print("Audio exists, skip extraction")
            else:
                audio_path = extract_audio(video_path, output_dir, self.audio_config)
        else:
            # Direct audio file - copy to output directory
            shutil.copy(input_path, output_dir)
            audio_path = os.path.join(output_dir, os.path.basename(input_path))
        
        return audio_path
    
    def _transcribe_with_model(self, model: str, audio_path: str, 
                              output_dir: str, metadata: Dict[str, Any]) -> str:
        """Transcribe audio with a specific model and inject metadata."""
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_file = os.path.join(output_dir, f'{base_name}-{model}.json')
        
        # Skip if transcript already exists
        if os.path.exists(transcript_file):
            print(f"Transcription exists ({model})")
            return transcript_file
        
        # Run transcription
        transcript_file = transcribe(
            model, audio_path, output_dir, self.model_configs.get(model, {})
        )
        
        # Inject metadata at the beginning of the JSON file
        self._inject_metadata(transcript_file, metadata, model)
        
        return transcript_file
    
    def _inject_metadata(self, transcript_file: str, metadata: Dict[str, Any], model: str):
        """Inject metadata at the beginning of the transcript JSON file."""
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create ordered dict with metadata first
            ordered = OrderedDict()
            ordered['title'] = metadata.get('title')
            ordered['description'] = metadata.get('description')
            ordered['uploader'] = metadata.get('uploader')
            ordered['upload_date'] = metadata.get('upload_date')
            ordered['video_id'] = metadata.get('id')
            ordered['model'] = model
            
            # Add remaining data
            for key, value in data.items():
                if key not in ordered:
                    ordered[key] = value
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                json.dump(ordered, f, indent=4, ensure_ascii=False)
        
        except Exception as e:
            print(f"Metadata inject failed ({model}): {e}")
    
    @staticmethod
    def _is_youtube_url(url: str) -> bool:
        """Check if the input is a YouTube URL."""
        return "youtube.com" in url or "youtu.be" in url