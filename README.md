# flersucker: A Transcription Tool

A Python-based transcription tool for audio and video files (local or YouTube).

## Features

- **Multiple Input Sources**: Transcribe local audio/video files (`.wav`, `.mp3`, `.mp4`) or download and transcribe from YouTube URLs and playlists.
- **Automatic Audio Extraction**: For video files, the audio is automatically extracted using `ffmpeg`.
- **Multiple Transcription Models**: Support for various speech-to-text models. Each model has its own script for modularity.
  - **whisper**: OpenAI Whisper (large-v3)
  - **whisperx**: WhisperX with forced alignment (large-v3)
  - **faster_whisper**: Faster implementation of Whisper (large-v3)
  - **parakeet**: NVIDIA Parakeet TDT-0.6b-v3 multilingual model (nvidia/parakeet-tdt-0.6b-v3)
  - **canary**: NVIDIA Canary multilingual model (nvidia/canary-1b)
- **GPU/CPU Support**: All models are configured to use GPU when available, with CPU fallback.
- **Configurable Model Parameters**: Model sizes, devices, and other parameters can be configured via `config.yaml`.
- **Timestamped Transcripts**: All transcripts include timestamps.
- **Multiple Output Formats**: Save transcripts in various formats like `json`, `srt`, and `csv`.
- **Consensus Function**: Automatically generate a consensus transcript by comparing the outputs of multiple models.
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
│   ├── consensus.py
│   ├── utils.py
│   └── models/
│       ├── whisper.py
│       ├── whisperx.py
│       ├── faster_whisper.py
│       ├── parakeet.py
│       └── canary.py
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
python main.py path/to/your/audio.mp3 --models whisper whisperx
```

**Transcribe a YouTube video:**

```bash
python main.py "https://www.youtube.com/watch?v=your_video_id" --models whisper parakeet
```

**Use all available models:**

```bash
python main.py audio.wav --models whisper whisperx faster_whisper parakeet canary
```

The tool will create an `output` directory with a subdirectory for each transcription job, named with the date and the title of the file/video.

## Configuration

You can configure the models and output formats in the `config.yaml` file. If you don't specify models via the command line, the tool will use the models listed in the config file. If no models are specified in either, you will be prompted to choose from the available models.

### Model Configuration

Each model can be individually configured with specific parameters:

```yaml
# config.yaml
models:
  - whisper
  - whisperx
  - faster_whisper
  - parakeet
  - canary

output_formats:
  - json
  - srt
  - csv

model_configs:
  whisper:
    model_size: "large-v3"
    device: "cuda"
  whisperx:
    model_size: "large-v3"
    device: "cuda"
    batch_size: 16
    compute_type: "float16"
  faster_whisper:
    model_size: "large-v3"
    device: "cuda"
    compute_type: "float16"
  parakeet:
    model_size: "nvidia/parakeet-tdt-0.6b-v3"
    device: "cuda"
  canary:
    model_size: "nvidia/canary-1b"
    device: "cuda"
```

### Available Models

- **whisper**: OpenAI's Whisper model with various size options (tiny, base, small, medium, large, large-v2, large-v3)
- **whisperx**: Enhanced Whisper with forced alignment for better timestamp accuracy
- **faster_whisper**: Optimized implementation of Whisper using CTranslate2
- **parakeet**: NVIDIA's TDT based ASR model, optimized for streaming applications
- **canary**: NVIDIA's multilingual ASR model supporting multiple languages

### Output Formats

The tool can generate transcripts in multiple formats:
- **JSON**: Detailed format with segments and timestamps
- **SRT**: Standard subtitle format
- **CSV**: Comma-separated values for data analysis

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
