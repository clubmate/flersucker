import argparse
import os
import yaml
import sys
import importlib.util
import json
from src.download import download_youtube_with_versions, extract_audio, probe_youtube, is_playlist, iter_playlist_entries
from src.transcribe import transcribe
from src.utils import create_output_directory

def apply_nemo_patch_on_windows():
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

def main():
    apply_nemo_patch_on_windows()
    parser = argparse.ArgumentParser(description="Transcription tool for audio / video / YouTube playlist (sequential).")
    parser.add_argument("input", help="Path to local file or YouTube URL / playlist")
    parser.add_argument("--models", nargs="+", default=[], help="Models to use")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--playlist-start", type=int, default=1, help="Start index (1-based) when processing a YouTube playlist")
    args = parser.parse_args()

    # Config
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    models = args.models or config.get("models", [])
    if not models:
        print("Available models: parakeet")
        models = input("Which model(s)? ").split()
    model_cfgs = config.get("model_configs", {})
    models = [m for m in models if model_cfgs.get(m, {}).get("active", True)]

    yt_cfg = config.get("youtube_download", {})
    video_quality = yt_cfg.get("video_quality", "best[ext=mp4]/best")
    additional_versions = yt_cfg.get("additional_versions", [])
    audio_config = yt_cfg.get("audio_extraction", {})

    def process_one(single_input, meta_override=None):
        out_dir = create_output_directory(single_input)
        meta = meta_override or {}
        video_path = None
        if "youtube.com" in single_input or "youtu.be" in single_input:
            print(f"Download: {single_input}")
            video_path, additional_video_paths, dl_meta = download_youtube_with_versions(
                single_input, out_dir, quality=video_quality, additional_versions=additional_versions
            )
            # Merge: overwrite empty/None values from flat playlist probe with real values
            for k, v in dl_meta.items():
                if k not in meta or not meta.get(k):  # also replaces '' or None
                    meta[k] = v
        elif single_input.endswith('.mp4'):
            import shutil
            shutil.copy(single_input, out_dir)
            video_path = os.path.join(out_dir, os.path.basename(single_input))
        # Audio path
        if video_path:
            audio_name = os.path.splitext(os.path.basename(video_path))[0] + '.wav'
            # Use the same directory as the video file for consistency
            video_dir = os.path.dirname(video_path)
            audio_path = os.path.join(video_dir, audio_name)
            if os.path.exists(audio_path):
                print("Audio exists, skip extraction")
            else:
                audio_path = extract_audio(video_path, video_dir, audio_config=audio_config)
        else:
            import shutil
            shutil.copy(single_input, out_dir)
            audio_path = os.path.join(out_dir, os.path.basename(single_input))
        if not meta:
            base_no_ext = os.path.splitext(os.path.basename(single_input))[0]
            meta = {'title': base_no_ext, 'description': '', 'uploader': '', 'upload_date': '', 'id': ''}
        transcripts = []
        for m in models:
            try:
                base_name = os.path.splitext(os.path.basename(audio_path))[0]
                # Use the same directory as the audio file for consistency
                audio_dir = os.path.dirname(audio_path)
                t_file = os.path.join(audio_dir, f'{base_name}-{m}.json')
                if os.path.exists(t_file):
                    print(f"Transcription exists ({m})")
                    transcripts.append(t_file)
                    continue
                t_file = transcribe(m, audio_path, audio_dir, model_cfgs.get(m, {}))
                # prepend metadata
                try:
                    from collections import OrderedDict
                    with open(t_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    ordered = OrderedDict()
                    ordered['title'] = meta.get('title')
                    ordered['description'] = meta.get('description')
                    ordered['uploader'] = meta.get('uploader')
                    ordered['upload_date'] = meta.get('upload_date')
                    ordered['video_id'] = meta.get('id')
                    ordered['model'] = m
                    for k, v in data.items():
                        if k in ordered:
                            continue
                        ordered[k] = v
                    with open(t_file, 'w', encoding='utf-8') as f:
                        json.dump(ordered, f, indent=4, ensure_ascii=False)
                except Exception as me:
                    print(f"Metadata inject failed ({m}): {me}")
                transcripts.append(t_file)
            except Exception as e:
                print(f"Model {m} error: {e}")
        return transcripts

    inp = args.input
    all_transcripts = []
    if "youtube.com" in inp or "youtu.be" in inp:
        try:
            info = probe_youtube(inp)
            if is_playlist(info):
                print(f"Playlist: {info.get('title')}")
                entries = list(iter_playlist_entries(info))
                total = len(entries)
                start_index = max(1, args.playlist_start)
                if start_index > total:
                    print(f"Start index {start_index} is greater than playlist length {total}. Nothing to do.")
                    return
                if start_index > 1:
                    print(f"Skipping first {start_index-1} videos. Starting at {start_index}/{total}.")
                for idx, entry in enumerate(entries, start=1):
                    if idx < start_index:
                        continue
                    url = entry.get('url')
                    if not url:
                        continue
                    title = entry.get('title') or entry.get('id') or 'Untitled'
                    print(f"\n{idx}/{total}: {title}")
                    meta = {
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'description': (entry.get('description') or ''),
                        'uploader': entry.get('uploader') or '',
                        'upload_date': entry.get('upload_date') or '',
                    }
                    all_transcripts.extend(process_one(url, meta_override=meta))
            else:
                all_transcripts.extend(process_one(inp))
        except Exception as e:
            print(f"Probe failed, fallback single: {e}")
            all_transcripts.extend(process_one(inp))
    else:
        all_transcripts.extend(process_one(inp))

if __name__ == "__main__":
    main()
