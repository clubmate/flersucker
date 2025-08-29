"""Download and audio extraction functionality."""

import yt_dlp
import ffmpeg
from pathlib import Path
from typing import Dict, Any, Optional


class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass


class AudioExtractionError(Exception):
    """Custom exception for audio extraction errors."""
    pass


def download_youtube(url: str, output_path: Path, quality: str = 'best[ext=mp4]/best') -> Path:
    """Download a YouTube video or playlist."""
    ydl_opts = {
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'format': quality,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = Path(ydl.prepare_filename(info))
            print(f"Downloaded: {downloaded_file.name}")
            return downloaded_file
            
    except Exception as e:
        raise DownloadError(f"Failed to download YouTube video: {e}")


def extract_audio(video_path: Path, output_path: Path, 
                 audio_config: Optional[Dict[str, Any]] = None) -> Path:
    """Extract audio from a video file using ffmpeg-python."""
    if audio_config is None:
        audio_config = {
            'acodec': 'pcm_s16le',
            'ar': 16000,
            'ac': 1
        }

    # Create output filename
    audio_filename = video_path.stem + '.wav'
    audio_path = output_path / audio_filename

    # Skip if audio file already exists
    if audio_path.exists():
        print(f"Audio file already exists: {audio_path}")
        return audio_path

    try:
        print(f"Extracting audio from {video_path.name}...")
        
        # Build ffmpeg pipeline
        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.output(
            stream,
            str(audio_path),
            acodec=audio_config.get('acodec', 'pcm_s16le'),
            ar=audio_config.get('ar', 16000),
            ac=audio_config.get('ac', 1),
            vn=None  # No video
        )
        
        # Run with error handling
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        print(f"Audio extracted to: {audio_path.name}")
        return audio_path
        
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode('utf8') if e.stderr else str(e)}"
        raise AudioExtractionError(error_msg)
    except Exception as e:
        raise AudioExtractionError(f"Unexpected error during audio extraction: {e}")
