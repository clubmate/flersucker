import yt_dlp
import os
import subprocess

def download_youtube(url, output_path):
    """
    Downloads a YouTube video or playlist.
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def extract_audio(video_path, output_path):
    """
    Extracts audio from a video file.
    """
    audio_filename = os.path.splitext(os.path.basename(video_path))[0] + '.mp3'
    audio_path = os.path.join(output_path, audio_filename)
    command = [
        'ffmpeg',
        '-i', video_path,
        '-q:a', '0',
        '-map', 'a',
        audio_path
    ]
    subprocess.run(command, check=True)
    return audio_path
