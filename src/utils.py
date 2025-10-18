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

def get_date_for_directory(input_path):
    """
    Gets the appropriate date for the output directory.
    For YouTube videos: upload date
    For local files: modification date
    Returns date in YYYYMMDD format.
    """
    if "youtube.com" in input_path or "youtu.be" in input_path:
        # Get upload date from YouTube
        ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(input_path, download=False)
            upload_date = info.get('upload_date')
            if upload_date:
                # upload_date is already in YYYYMMDD format
                return upload_date
            else:
                # Fallback to current date if upload_date not available
                return datetime.datetime.now().strftime("%Y%m%d")
    else:
        # For local files, use modification date
        if os.path.exists(input_path):
            # Use modification time (Änderungsdatum) instead of creation time
            mod_time = os.path.getmtime(input_path)
            return datetime.datetime.fromtimestamp(mod_time).strftime("%Y%m%d")
        else:
            # Fallback to current date
            return datetime.datetime.now().strftime("%Y%m%d")

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.
    Removes all special characters, keeps only a-z letters and 0-9 numbers, replaces spaces with hyphens.
    """
    if not name:
        return "unnamed"

    # Convert to lowercase
    name = name.lower()

    # Remove all characters that are not letters, numbers, or spaces
    name = re.sub(r'[^a-z0-9\s]', '', name)

    # Replace spaces with hyphens
    name = re.sub(r'\s+', '-', name)

    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)

    # Remove leading and trailing hyphens
    name = name.strip('-')

    # Ensure we have at least some content
    if not name:
        return "unnamed"

    return name

def create_output_directory(input_path, base_output_path='output'):
    """
    Creates an output directory based on the input file name or URL.
    """
    if "youtube.com" in input_path or "youtu.be" in input_path:
        title = get_youtube_title(input_path)
    else:
        title = os.path.splitext(os.path.basename(input_path))[0]

    sanitized_title = sanitize_filename(title)
    date_str = get_date_for_directory(input_path)
    dir_name = f"{date_str}-{sanitized_title[:40]}"  # Date is already in YYYYMMDD format
    
    # Ensure the main output directory exists
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path)

    output_dir = os.path.join(base_output_path, dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
