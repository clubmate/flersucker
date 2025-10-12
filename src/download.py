import yt_dlp
import os
import ffmpeg

def download_youtube(url, output_path, quality='best[ext=mp4]/best', custom_template=None):
    """Download a YouTube video and return (filepath, metadata dict).

    The metadata dict contains (subset of yt_dlp info):
      id, title, description, uploader, upload_date, webpage_url
    """
    # Get the title first to create a clean filename
    probe_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        raw_title = info.get('title', 'youtube_video')

    # Import here to avoid circular imports
    from .utils import sanitize_filename
    clean_title = sanitize_filename(raw_title)

    # Use custom template if provided, otherwise use default
    if custom_template:
        template = custom_template.replace('{title}', clean_title)
    else:
        template = f'{clean_title}.%(ext)s'

    ydl_opts = {
        'outtmpl': os.path.join(output_path, template),
        'format': quality,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        
        # Convert upload_date from YYYYMMDD to DD.MM.YYYY format
        upload_date_raw = info.get('upload_date')
        upload_date_formatted = ''
        if upload_date_raw and len(upload_date_raw) == 8:
            # Convert YYYYMMDD to DD.MM.YYYY
            year = upload_date_raw[:4]
            month = upload_date_raw[4:6]
            day = upload_date_raw[6:8]
            upload_date_formatted = f"{day}.{month}.{year}"
        
        metadata = {
            'id': info.get('id'),
            'title': info.get('title'),
            'description': info.get('description'),
            'uploader': info.get('uploader'),
            'upload_date': upload_date_formatted,  # Now in DD.MM.YYYY format
        }
        return file_path, metadata

def download_youtube_with_versions(url, output_path, quality='best[ext=mp4]/best', additional_versions=None):
    """Download a YouTube video in multiple versions and return (best_filepath, additional_filepaths, metadata dict).

    additional_versions should be a list of dicts with keys:
      - quality: descriptive name (e.g., '480p')
      - format: yt-dlp format selector
      - convert_from_best: if True, convert from best quality instead of downloading separately
    """
    if additional_versions is None:
        additional_versions = []

    # First download the best quality version
    print(f"Downloading best quality version...")
    best_path, metadata = download_youtube(url, output_path, quality)

    additional_paths = {}

    for version_config in additional_versions:
        quality_name = version_config['quality']
        format_selector = version_config['format']
        convert_from_best = version_config.get('convert_from_best', False)

        if convert_from_best:
            # Convert from the best quality video
            print(f"Converting to {quality_name}...")
            converted_path = convert_video_to_quality(best_path, quality_name)
            if converted_path:
                additional_paths[quality_name] = converted_path
        else:
            # Download separately with custom template to avoid filename conflicts
            print(f"Downloading {quality_name} version...")
            custom_template = f'{{title}}_{quality_name}.%(ext)s'
            version_path, _ = download_youtube(url, output_path, format_selector, custom_template=custom_template)
            additional_paths[quality_name] = version_path

    return best_path, additional_paths, metadata

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
        
        # Convert upload_date from YYYYMMDD to DD.MM.YYYY format
        upload_date_raw = entry.get('upload_date')
        upload_date_formatted = ''
        if upload_date_raw and len(upload_date_raw) == 8:
            # Convert YYYYMMDD to DD.MM.YYYY
            year = upload_date_raw[:4]
            month = upload_date_raw[4:6]
            day = upload_date_raw[6:8]
            upload_date_formatted = f"{day}.{month}.{year}"
        
        yield {
            'id': vid,
            'title': entry.get('title'),
            'uploader': entry.get('uploader'),
            'upload_date': upload_date_formatted,  # Now in DD.MM.YYYY format
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
        print(f"Extracting audio from: {video_path}")
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

def convert_video_to_quality(input_video_path, target_quality):
    """
    Convert a video to a specific quality using ffmpeg.
    Supports 480p conversion with optimized settings.
    """
    if target_quality.lower() == '480p':
        # Set output resolution to 854x480 (480p)
        width = 854
        height = 480
    else:
        print(f"Unsupported quality: {target_quality}")
        return None

    output_filename = os.path.splitext(os.path.basename(input_video_path))[0] + f'_{target_quality}.mp4'
    output_path = os.path.join(os.path.dirname(input_video_path), output_filename)

    # Skip if already exists
    if os.path.exists(output_path):
        print(f"Converted video already exists: {output_path}")
        return output_path

    try:
        print(f"Converting {input_video_path} to {target_quality}...")

        # Optimized FFmpeg command for 480p conversion
        (
            ffmpeg
            .input(input_video_path)
            .output(output_path,
                   # Video filters: scale with aspect ratio preservation and padding
                   vf=f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                   # Video codec settings
                   vcodec='libx264',  # H.264 codec
                   preset='medium',   # Good balance between speed and quality
                   crf=23,           # Constant quality (lower = better quality, higher = smaller file)
                   # Audio settings
                   acodec='aac',     # AAC audio codec
                   ab='128k',        # Audio bitrate
                   ar=44100,         # Audio sample rate
                   ac=2,             # Stereo audio
                   # Additional optimizations
                   movflags='+faststart',  # Enable fast start for web playback
                   pix_fmt='yuv420p'       # Pixel format for compatibility
                   )
            .global_args('-progress', 'pipe:1')  # Output progress to stdout
            .run(capture_stdout=False, capture_stderr=False, overwrite_output=True)
        )
        print(f"Conversion complete: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        print('Conversion stdout:', e.stdout.decode('utf8'))
        print('Conversion stderr:', e.stderr.decode('utf8'))
        return None
