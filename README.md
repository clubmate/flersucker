# flersucker: A Transcription Tool

A Python-based transcription tool for audio and video files (local or YouTube).

## Features

- **Multiple Input Sources**: Transcribe local audio/video files (`.wav`, `.mp3`, `.mp4`) or download and transcribe from YouTube URLs and playlists.
- **Sequential Playlist Processing**: Playlists werden Video für Video nacheinander verarbeitet (Download -> Audio-Extraktion -> Transkription), keine Massen-Downloads vorab.
- **Playlist Fortschritt & Offset**: Fortschrittsanzeige `>>> 4/200: Titel` und Start ab beliebigem Index via `--playlist-start`.
- **Automatic Audio Extraction**: For video files, the audio is automatically extracted using `ffmpeg`.
- **Multiple Transcription Models**: Support for various speech-to-text models. Each model has its own script for modularity.
  - **parakeet**: NVIDIA Parakeet TDT-0.6b-v3 multilingual model (nvidia/parakeet-tdt-0.6b-v3)
- **GPU/CPU Support**: All models are configured to use GPU when available, with CPU fallback.
- **Configurable Model Parameters**: Model sizes, devices, and other parameters can be configured via `config.yaml`.
- **Timestamped Transcripts**: All transcripts include timestamps (word-level and segment-level).
- **Configurable**: Configure the tool via command-line arguments or a `config.yaml` file.

## Project Structure

```
flersucker/
├── main.py
├── config.yaml
├── requirements.txt
├── src/
│   ├── download.py
│   ├── transcribe.py
│   ├── utils.py
│   └── models/
│       ├── model_example.py
│       └── model_parakeet.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- ffmpeg
- CUDA-compatible GPU (recommended for optimal performance)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/clubmate/flersucker.git
    cd flersucker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main script with the path to your local file or a YouTube URL.

**Transcribe a local file:**

```bash
python main.py path/to/your/audio.mp3 --models parakeet
```

**Transcribe a YouTube video:**

```bash
python main.py "https://www.youtube.com/watch?v=your_video_id" --models parakeet
```

**Transcribe a YouTube playlist (sequential):**

```bash
python main.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --models parakeet
```

Während der Verarbeitung wird jede Episode mit numerischem Fortschritt ausgegeben:

```
>>> 4/200: Joey Bada$$ - DARK AURA (Official Video)
```

**Playlist ab bestimmtem Video starten (Skip erster N-1 Videos):**

```bash
python main.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --models parakeet --playlist-start 7
```

Startindex ist 1-basiert; bei `--playlist-start 7` beginnt die Verarbeitung mit dem 7. Video.

**Use all available models:**

```bash
python main.py audio.wav --models parakeet
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
  - srt
  - csv

model_configs:
  parakeet:
    model_size: "nvidia/parakeet-tdt-0.6b-v3"
    device: "cuda"
```

### Available Models

- **parakeet**: NVIDIA's TDT based ASR model, optimized for streaming applications

### Output Formats

The tool can generate transcripts in multiple formats:
- **JSON**: Detailed format with segments and timestamps
- **SRT**: Standard subtitle format
- **CSV**: Comma-separated values for data analysis

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
