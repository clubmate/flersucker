"""
Playlist processing module for handling YouTube playlists.
"""
from typing import List, Dict, Any

from .download import probe_youtube, is_playlist, iter_playlist_entries
from .processor import TranscriptionProcessor


class PlaylistProcessor:
    """Handles processing of YouTube playlists."""
    
    def __init__(self, transcription_processor: TranscriptionProcessor):
        self.transcription_processor = transcription_processor
    
    def process_playlist(self, url: str, start_index: int = 1) -> List[str]:
        """
        Process a YouTube playlist starting from the specified index.
        
        Args:
            url: YouTube playlist URL
            start_index: 1-based index to start processing from
            
        Returns:
            List of all generated transcript files
        """
        try:
            info = probe_youtube(url)
            if not is_playlist(info):
                # Not a playlist, process as single video
                return self.transcription_processor.process(url)
            
            return self._process_playlist_entries(info, start_index)
        
        except Exception as e:
            print(f"Playlist probe failed, processing as single video: {e}")
            return self.transcription_processor.process(url)
    
    def _process_playlist_entries(self, playlist_info: Dict[str, Any], start_index: int) -> List[str]:
        """Process individual entries in a playlist."""
        print(f"Playlist: {playlist_info.get('title', 'Unknown')}")
        
        entries = list(iter_playlist_entries(playlist_info))
        total = len(entries)
        
        if start_index > total:
            print(f"Start index {start_index} is greater than playlist length {total}. Nothing to do.")
            return []
        
        if start_index > 1:
            print(f"Skipping first {start_index-1} videos. Starting at {start_index}/{total}.")
        
        all_transcripts = []
        
        for idx, entry in enumerate(entries, start=1):
            if idx < start_index:
                continue
            
            url = entry.get('url')
            if not url:
                continue
            
            title = entry.get('title') or entry.get('id') or 'Untitled'
            print(f"\n{idx}/{total}: {title}")
            
            metadata = {
                'id': entry.get('id'),
                'title': entry.get('title'),
                'description': entry.get('description') or '',
                'uploader': entry.get('uploader') or '',
                'upload_date': entry.get('upload_date') or '',
            }
            
            try:
                transcripts = self.transcription_processor.process(url, metadata_override=metadata)
                all_transcripts.extend(transcripts)
            except Exception as e:
                print(f"Error processing video {idx}: {e}")
        
        return all_transcripts