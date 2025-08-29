import os
import sys
import datetime
import re
import yaml
import importlib.util
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
    date_str = get_date_for_directory(input_path)
    dir_name = f"{date_str}-{sanitized_title[:40]}"  # Date is already in YYYYMMDD format
    
    # Ensure the main output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    output_dir = os.path.join('output', dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def apply_nemo_patch_on_windows():
    """Apply Windows compatibility patch for nemo_toolkit."""
    if sys.platform != "win32":
        return
    try:
        spec = importlib.util.find_spec("nemo")
        if spec is None or spec.origin is None:
            return
        nemo_dir = os.path.dirname(spec.origin)
        exp_manager_path = os.path.join(nemo_dir, 'utils', 'exp_manager.py')
        if not os.path.exists(exp_manager_path):
            return
        with open(exp_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        old_line = "rank_termination_signal: signal.Signals = signal.SIGKILL"
        if old_line in content:
            new_line = "rank_termination_signal: signal.Signals = signal.SIGTERM"
            with open(exp_manager_path, 'w', encoding='utf-8') as f:
                f.write(content.replace(old_line, new_line))
            print("Applied patch to nemo_toolkit for Windows compatibility.")
    except Exception as e:
        print(f"Could not apply nemo_toolkit patch: {e}")


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def get_active_models(args_models, config):
    """Get list of active models from args or config."""
    models = args_models or config.get("models", [])
    if not models:
        print("Available models: parakeet")
        models = input("Which model(s)? ").split()
    
    model_cfgs = config.get("model_configs", {})
    return [m for m in models if model_cfgs.get(m, {}).get("active", True)]
