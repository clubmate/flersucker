"""
Main entry point for the transcription tool.
"""
from src.cli import parse_args
from src.utils import apply_nemo_patch_on_windows, load_config, get_active_models
from src.processor import TranscriptionProcessor
from src.playlist import PlaylistProcessor


def main():
    """Main function to orchestrate the transcription process."""
    # Apply Windows compatibility patch if needed
    apply_nemo_patch_on_windows()
    
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration
    config = load_config(args['config'])
    
    # Get active models
    models = get_active_models(args['models'], config)
    if not models:
        print("No active models found. Exiting.")
        return
    
    # Get configuration settings
    model_configs = config.get("model_configs", {})
    yt_config = config.get("youtube_download", {})
    video_quality = yt_config.get("video_quality", "best[ext=mp4]/best")
    audio_config = yt_config.get("audio_extraction", {})
    
    # Create processor instances
    transcription_processor = TranscriptionProcessor(
        models=models,
        model_configs=model_configs,
        video_quality=video_quality,
        audio_config=audio_config
    )
    
    # Process input
    input_path = args['input']
    
    if _is_youtube_url(input_path):
        # Use playlist processor for YouTube URLs (handles both playlists and single videos)
        playlist_processor = PlaylistProcessor(transcription_processor)
        all_transcripts = playlist_processor.process_playlist(
            input_path, 
            start_index=args['playlist_start']
        )
    else:
        # Process local file directly
        all_transcripts = transcription_processor.process(input_path)
    
    # Print summary
    if all_transcripts:
        print(f"\nCompleted! Generated {len(all_transcripts)} transcript files:")
        for transcript in all_transcripts:
            print(f"  {transcript}")
    else:
        print("\nNo transcripts were generated.")


def _is_youtube_url(url: str) -> bool:
    """Check if the input is a YouTube URL."""
    return "youtube.com" in url or "youtu.be" in url


if __name__ == "__main__":
    main()
