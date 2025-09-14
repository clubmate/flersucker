import yt_dlp
import os
import ffmpeg

def download_youtube(url, output_path, quality='best[ext=mp4]/best'):
    """Download a YouTube video and return (filepath, metadata dict).

    The metadata dict contains (subset of yt_dlp info):
      id, title, description, uploader, upload_date, webpage_url
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
            'upload_date': info.get('upload_date'),  # YYYYMMDD
        }
        return file_path, metadata

def probe_youtube(url):
    """Return raw yt_dlp info dict without downloading (flat where possible)."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def is_playlist(info_dict):
    return isinstance(info_dict, dict) and info_dict.get('_type') == 'playlist' and 'entries' in info_dict

def iter_playlist_entries(info_dict):
    """Yield minimal entry dicts from a probed playlist info dict."""
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

def extract_audio(video_path, output_path=None, audio_config=None):
    """
    Extracts audio from a video file based on the provided config using ffmpeg-python.
    If output_path is None, saves the audio in the same directory as the video.
    """
    if audio_config is None:
        audio_config = {}

    acodec = audio_config.get('acodec', 'pcm_s16le')
    ar = audio_config.get('ar', 16000)
    ac = audio_config.get('ac', 1)

    audio_filename = os.path.splitext(os.path.basename(video_path))[0] + '.wav'
    
    # Use the directory of the video file if no output_path is specified
    if output_path is None:
        output_path = os.path.dirname(video_path)
    
    audio_path = os.path.join(output_path, audio_filename)

    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec=acodec, ar=ar, ac=ac, vn=None)
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

    return audio_path
