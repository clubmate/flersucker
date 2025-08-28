import yt_dlp
import os
import ffmpeg

def download_youtube(url, output_path, quality='best[ext=mp4]/best'):
    """
    Downloads a YouTube video or playlist.
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': quality,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def extract_audio(video_path, output_path, audio_config=None):
    """
    Extracts audio from a video file based on the provided config using ffmpeg-python.
    """
    if audio_config is None:
        audio_config = {}

    acodec = audio_config.get('acodec', 'pcm_s16le')
    ar = audio_config.get('ar', 16000)
    ac = audio_config.get('ac', 1)

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
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

    return audio_path
