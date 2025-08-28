# flersucker: A Transcription Tool

A Python-based transcription tool for audio and video files (local or YouTube).

## Features

- **Multiple Input Sources**: Transcribe local audio/video files (`.wav`, `.mp3`, `.mp4`) or download and transcribe from YouTube URLs and playlists.
- **Automatic Audio Extraction**: For video files, the audio is automatically extracted using `ffmpeg`.
- **Multiple Transcription Models**: Support for various speech-to-text models. Each model has its own script for modularity.
  - whisper
  - whisperx
  - faster_whisper
  - parakeet
  - phi
  - canary
  - voxtral
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
│       ├── phi.py
│       ├── canary.py
│       └── voxtral.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- ffmpeg

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
python main.py "https://www.youtube.com/watch?v=your_video_id" --models whisper
```

The tool will create an `output` directory with a subdirectory for each transcription job, named with the date and the title of the file/video.

## Configuration

You can configure the models and output formats in the `config.yaml` file. If you don't specify models via the command line, the tool will use the models listed in the config file. If no models are specified in either, you will be prompted to choose from the available models.

```yaml
# config.yaml
models:
  - whisper
  - whisperx

output_formats:
  - json
  - srt
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
