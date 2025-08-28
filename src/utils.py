import os
import datetime
import re
import yt_dlp

def get_youtube_title(url):
    """
    Gets the title of a YouTube video without downloading it.
    """
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'youtube_video')

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.
    """
    return re.sub(r'[\\/*?:"<>|]',"", name)

def create_output_directory(input_path):
    """
    Creates an output directory based on the input file name or URL.
    """
    if "youtube.com" in input_path or "youtu.be" in input_path:
        title = get_youtube_title(input_path)
    else:
        title = os.path.splitext(os.path.basename(input_path))[0]

    sanitized_title = sanitize_filename(title)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_name = f"{date_str}_{sanitized_title[:20]}"
    
    # Ensure the main output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    output_dir = os.path.join('output', dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
