"""Utility functions for file handling and configuration."""

import re
import yt_dlp
from pathlib import Path
from datetime import datetime
from typing import Optional


def get_youtube_title(url: str) -> str:
    """Get the title of a YouTube video without downloading it."""
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title', 'youtube_video')
    except Exception as e:
        print(f"Warning: Could not extract YouTube title: {e}")
        return 'youtube_video'


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """Sanitize a string to be used as a valid filename."""
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    # Remove extra whitespace and limit length
    sanitized = re.sub(r'\s+', '_', sanitized.strip())
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized


def is_youtube_url(url: str) -> bool:
    """Check if the given string is a YouTube URL."""
    return "youtube.com" in url or "youtu.be" in url


def is_video_file(file_path: str) -> bool:
    """Check if the file is a video file based on extension."""
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
    return Path(file_path).suffix.lower() in video_extensions


def is_audio_file(file_path: str) -> bool:
    """Check if the file is an audio file based on extension."""
    audio_extensions = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a'}
    return Path(file_path).suffix.lower() in audio_extensions


def create_output_directory(input_path: str, base_dir: str = "output") -> Path:
    """Create an output directory based on the input file name or URL."""
    # Determine the title/name
    if is_youtube_url(input_path):
        title = get_youtube_title(input_path)
    else:
        title = Path(input_path).stem
    
    # Create sanitized directory name
    sanitized_title = sanitize_filename(title, max_length=30)
    date_str = datetime.now().strftime("%Y-%m-%d")
    dir_name = f"{date_str}_{sanitized_title}"
    
    # Create the output directory
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True)
    
    output_dir = base_path / dir_name
    output_dir.mkdir(exist_ok=True)
    
    return output_dir


def copy_file_to_directory(file_path: str, target_dir: Path) -> Path:
    """Copy a file to target directory and return the new path."""
    import shutil
    
    source_path = Path(file_path)
    target_path = target_dir / source_path.name
    
    if not target_path.exists():
        shutil.copy2(source_path, target_path)
    
    return target_path
