import os
import datetime

def create_output_directory(input_path):
    """
    Creates an output directory based on the input file name or URL.
    """
    if "youtube.com" in input_path or "youtu.be" in input_path:
        # It's a youtube link, we need to get the title
        # For now, let's use a generic name.
        # A better approach would be to get the title before downloading.
        title = "youtube_video"
    else:
        title = os.path.splitext(os.path.basename(input_path))[0]

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_name = f"{date_str}_{title[:20]}"
    
    # Ensure the main output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    output_dir = os.path.join('output', dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
