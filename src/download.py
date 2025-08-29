"""
Download and audio extraction utilities for YouTube videos and local files.
"""
import os
from typing import Dict, Any, Tuple, Optional, Generator

import yt_dlp
import ffmpeg


def download_youtube(url: str, output_path: str, quality: str = 'best[ext=mp4]/best') -> Tuple[str, Dict[str, Any]]:
    """
    Download a YouTube video and return filepath and metadata.

    Args:
        url: YouTube video URL
        output_path: Directory to save the downloaded video
        quality: Video quality format string for yt-dlp

    Returns:
        Tuple of (filepath, metadata dict) where metadata contains:
        id, title, description, uploader, upload_date
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': quality,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        metadata = {
            'id': info.get('id'),
            'title': info.get('title'),
            'description': info.get('description'),
            'uploader': info.get('uploader'),
            'upload_date': info.get('upload_date'),  # YYYYMMDD format
        }
        return file_path, metadata


def probe_youtube(url: str) -> Dict[str, Any]:
    """
    Get YouTube video/playlist info without downloading.
    
    Args:
        url: YouTube URL to probe
        
    Returns:
        Raw yt-dlp info dictionary
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def is_playlist(info_dict: Dict[str, Any]) -> bool:
    """Check if the yt-dlp info dict represents a playlist."""
    return (isinstance(info_dict, dict) and 
            info_dict.get('_type') == 'playlist' and 
            'entries' in info_dict)


def iter_playlist_entries(info_dict: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Yield minimal entry dicts from a probed playlist info dict.
    
    Args:
        info_dict: yt-dlp info dictionary from probe_youtube
        
    Yields:
        Dictionary with keys: id, title, uploader, upload_date, description, url
    """
    if not is_playlist(info_dict):
        return
    
    for entry in info_dict.get('entries', []) or []:
        if not entry:
            continue
        
        vid = entry.get('id')
        url = entry.get('url') or (f"https://www.youtube.com/watch?v={vid}" if vid else None)
        
        yield {
            'id': vid,
            'title': entry.get('title'),
            'uploader': entry.get('uploader'),
            'upload_date': entry.get('upload_date'),
            'description': entry.get('description'),
            'url': url,
        }


def extract_audio(video_path: str, output_path: str, audio_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Extract audio from a video file using ffmpeg.
    
    Args:
        video_path: Path to the input video file
        output_path: Directory to save the extracted audio
        audio_config: Audio extraction configuration
        
    Returns:
        Path to the extracted audio file
        
    Raises:
        ffmpeg.Error: If audio extraction fails
    """
    if audio_config is None:
        audio_config = {}

    # Default audio settings optimized for speech recognition
    acodec = audio_config.get('acodec', 'pcm_s16le')
    ar = audio_config.get('ar', 16000)  # 16kHz sample rate
    ac = audio_config.get('ac', 1)      # mono channel

    audio_filename = os.path.splitext(os.path.basename(video_path))[0] + '.wav'
    audio_path = os.path.join(output_path, audio_filename)

    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec=acodec, ar=ar, ac=ac, vn=None)
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print(f"FFmpeg stdout: {e.stdout.decode('utf8')}")
        print(f"FFmpeg stderr: {e.stderr.decode('utf8')}")
        raise

    return audio_path
