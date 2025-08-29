"""Configuration management for the transcription tool."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class ConfigManager:
    """Manages configuration loading and validation."""
    
    DEFAULT_CONFIG = {
        'models': ['whisper'],
        'output_formats': ['json'],
        'model_configs': {
            'whisper': {
                'model_size': 'large-v3',
                'device': 'cuda'
            },
            'parakeet': {
                'model_name': 'nvidia/parakeet-tdt-0.6b-v3',
                'device': 'cuda'
            },
            'canary': {
                'model_name': 'nvidia/canary-1b',
                'device': 'cuda'
            }
        },
        'youtube_download': {
            'video_quality': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'audio_extraction': {
                'acodec': 'pcm_s16le',
                'ar': 16000,
                'ac': 1
            }
        }
    }
    
    AVAILABLE_MODELS = ['whisper', 'whisperx', 'faster_whisper', 'parakeet', 'canary']
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_path = Path(config_path) if config_path else Path('config.yaml')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                # Merge with defaults
                return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"Warning: Error loading config file {self.config_path}: {e}")
                print("Using default configuration.")
                return self.DEFAULT_CONFIG.copy()
        else:
            print(f"Config file {self.config_path} not found. Using defaults.")
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with defaults."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_models(self, cli_models: List[str]) -> List[str]:
        """Get the list of models to use, prioritizing CLI arguments."""
        if cli_models:
            return cli_models
        
        config_models = self.config.get('models', [])
        if config_models:
            return config_models
        
        # Interactive selection
        return self._prompt_for_models()
    
    def _prompt_for_models(self) -> List[str]:
        """Prompt user to select models interactively."""
        print(f"Available models: {', '.join(self.AVAILABLE_MODELS)}")
        while True:
            try:
                models_input = input("Which model(s) do you want to use? (space-separated): ").strip()
                if not models_input:
                    continue
                
                selected_models = models_input.split()
                
                # Validate models
                invalid_models = [m for m in selected_models if m not in self.AVAILABLE_MODELS]
                if invalid_models:
                    print(f"Invalid models: {', '.join(invalid_models)}")
                    print(f"Available models: {', '.join(self.AVAILABLE_MODELS)}")
                    continue
                
                return selected_models
                
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return ['whisper']  # Default fallback
    
    def get_model_config(self, model: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        model_configs = self.config.get('model_configs', {})
        return model_configs.get(model, {})
    
    def get_youtube_config(self) -> Dict[str, Any]:
        """Get YouTube download configuration."""
        return self.config.get('youtube_download', {})
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio extraction configuration."""
        youtube_config = self.get_youtube_config()
        return youtube_config.get('audio_extraction', {})
    
    def get_video_quality(self) -> str:
        """Get video quality setting for YouTube downloads."""
        youtube_config = self.get_youtube_config()
        return youtube_config.get('video_quality', 'best[ext=mp4]/best')
    
    def save_config(self, path: Optional[Path] = None) -> None:
        """Save current configuration to file."""
        save_path = path or self.config_path
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            print(f"Configuration saved to {save_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")