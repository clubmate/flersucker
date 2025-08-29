# flersucker: A Transcription Tool

A Python-based transcription tool for audio and video files (local or YouTube), featuring a modular architecture and support for multiple speech-to-text models.

## Features

- **Multiple Input Sources**: Transcribe local audio/video files (`.wav`, `.mp3`, `.mp4`) or download and transcribe from YouTube URLs and playlists.
- **Sequential Playlist Processing**: Playlists are processed video by video sequentially (Download → Audio Extraction → Transcription), no bulk downloads beforehand.
- **Playlist Progress & Offset**: Progress display `>>> 4/200: Title` and start from any index via `--playlist-start`.
- **Automatic Audio Extraction**: For video files, audio is automatically extracted using `ffmpeg`.
- **Multiple Transcription Models**: Support for various speech-to-text models. Each model has its own script for modularity.
  - **parakeet**: NVIDIA Parakeet TDT-0.6b-v3 multilingual model (nvidia/parakeet-tdt-0.6b-v3)
  - **example**: Demonstration model for testing and development
- **GPU/CPU Support**: All models are configured to use GPU when available, with CPU fallback.
- **Configurable Model Parameters**: Model sizes, devices, and other parameters can be configured via `config.yaml`.
- **Timestamped Transcripts**: All transcripts include timestamps (word-level and segment-level).
- **Configurable**: Configure the tool via command-line arguments or a `config.yaml` file.

## Project Structure

```
flersucker/
├── main.py                 # Main entry point
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── src/
│   ├── cli.py             # Command-line interface
│   ├── processor.py       # Main transcription processor
│   ├── playlist.py        # YouTube playlist handling
│   ├── download.py        # YouTube download utilities
│   ├── transcribe.py      # Model transcription interface
│   ├── utils.py           # Utility functions
│   └── models/
│       ├── model_example.py   # Example/test model
│       └── model_parakeet.py  # NVIDIA Parakeet model
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- ffmpeg
- CUDA-compatible GPU (recommended for optimal performance with ML models)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/clubmate/flersucker.git
    cd flersucker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

    **For GPU support (CUDA):**
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    ```

    **For CPU-only:**
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```

## Usage

### Basic Usage

**Transcribe a local audio file:**

```bash
python main.py audio.wav --models parakeet
```

**Transcribe a YouTube video:**

```bash
python main.py "https://youtube.com/watch?v=..." --models parakeet
```

**Process a YouTube playlist starting from a specific video:**

```bash
python main.py "https://youtube.com/playlist?list=..." --playlist-start 7 --models parakeet
```

Start index is 1-based; with `--playlist-start 7` processing begins with the 7th video.

**Use multiple models:**

```bash
python main.py audio.wav --models parakeet example
```

**Use example model for testing:**

```bash
python main.py audio.wav --models example
```

The tool will create an `output` directory with a subdirectory for each transcription job, named with the date and the title of the file/video.

## Configuration

You can configure the models and output formats in the `config.yaml` file. If you don't specify models via the command line, the tool will use the models listed in the config file. If no models are specified in either, you will be prompted to choose from the available models.

### Model Configuration

Each model can be individually configured with specific parameters:

```yaml
# config.yaml
models:
  - parakeet

output_formats:
  - json

model_configs:
  parakeet:
    active: true
    model_name: "nvidia/parakeet-tdt-0.6b-v3"
    device: "cuda"
  example:
    active: true

youtube_download:
  video_quality: "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
  audio_extraction:
    acodec: "pcm_s16le"
    ar: 16000 # sampling rate
    ac: 1 # mono
```

### Available Models

- **parakeet**: NVIDIA's TDT based ASR model, optimized for streaming applications
- **example**: Demonstration model for testing and development

### Output Formats

The tool generates transcripts in JSON format with the following structure:

```json
{
  "title": "Video Title",
  "description": "Video Description",
  "uploader": "Channel Name",
  "upload_date": "20231201",
  "video_id": "youtube_video_id",
  "model": "parakeet",
  "text": "Full transcript text",
  "language": "auto",
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "Segment text",
      "words": [
        {
          "start": 0.0,
          "end": 0.5,
          "word": "Word"
        }
      ]
    }
  ]
}
```

## Development

### Adding New Models

To add a new transcription model:

1. Create a new script in `src/models/` following the naming pattern `model_<name>.py`
2. Implement the required function signature:
   ```python
   def transcribe_<name>(input_file: str, output_file: str, config: Dict[str, Any]):
       # Your implementation here
   ```
3. Add the model configuration to `config.yaml`
4. The model will be automatically available in the CLI

### Project Architecture

The tool follows a modular architecture:

- **CLI Layer** (`src/cli.py`): Handles command-line argument parsing
- **Processing Layer** (`src/processor.py`): Core transcription workflow
- **Download Layer** (`src/download.py`): YouTube download and audio extraction
- **Model Layer** (`src/models/`): Individual model implementations
- **Utilities** (`src/utils.py`): Shared utility functions

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
