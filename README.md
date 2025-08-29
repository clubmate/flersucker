# flersucker: A Simple and Elegant Transcription Tool

A Python-based transcription tool for audio and video files (local or YouTube). Designed with simplicity, elegance, and modularity in mind.

## Features

- **Multiple Input Sources**: Transcribe local audio/video files (`.wav`, `.mp3`, `.mp4`) or download and transcribe from YouTube URLs and playlists.
- **Automatic Audio Extraction**: For video files, the audio is automatically extracted using `ffmpeg`.
- **Multiple Transcription Models**: Support for various speech-to-text models with modular architecture:
  - **whisper**: OpenAI Whisper (large-v3)
  - **parakeet**: NVIDIA Parakeet TDT-0.6b-v3 multilingual model (nvidia/parakeet-tdt-0.6b-v3)
  - **canary**: NVIDIA Canary multilingual model (nvidia/canary-1b)
- **GPU/CPU Support**: All models are configured to use GPU when available, with CPU fallback.
- **Intelligent Consensus**: Advanced word-level voting algorithm creates consensus transcripts from multiple models.
- **Configurable Model Parameters**: Model sizes, devices, and other parameters can be configured via `config.yaml`.
- **Timestamped Transcripts**: All transcripts include timestamps where available.
- **Multiple Output Formats**: Save transcripts in various formats like `json`, `srt`, and `csv`.
- **Enhanced CLI**: Rich command-line interface with validation and helpful examples.
- **Type Safety**: Comprehensive type hints throughout the codebase.
- **Error Handling**: Robust error handling with custom exceptions and detailed error messages.

## Architecture

The refactored codebase follows clean architecture principles:

```
flersucker/
├── main.py                    # Simple entry point
├── config.yaml               # Configuration file
├── requirements.txt
├── src/
│   ├── cli.py                # Command-line interface
│   ├── config.py             # Configuration management
│   ├── workflow.py           # Main workflow orchestrator
│   ├── download.py           # YouTube download & audio extraction
│   ├── transcribe.py         # Transcription orchestration
│   ├── consensus.py          # Advanced consensus algorithms
│   ├── utils.py              # Utility functions
│   └── models/
│       ├── __init__.py       # Models package
│       ├── base.py           # Base transcription model class
│       ├── model_whisper.py  # Whisper implementation
│       ├── model_parakeet.py # Parakeet implementation
│       └── model_canary.py   # Canary implementation
└── README.md
```

### Key Design Principles

1. **Modular Architecture**: Clear separation of concerns with focused modules
2. **DRY (Don't Repeat Yourself)**: Base classes eliminate code duplication
3. **Type Safety**: Comprehensive type hints improve code clarity and IDE support
4. **Error Handling**: Custom exceptions and graceful error recovery
5. **Configuration Management**: Centralized configuration with validation
6. **Testability**: Modular design makes unit testing straightforward

## Getting Started

### Prerequisites

- Python 3.8 or higher
- ffmpeg (for audio extraction)
- CUDA-compatible GPU (optional, for faster transcription)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/clubmate/flersucker.git
   cd flersucker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install PyTorch with CUDA support (optional but recommended):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

## Usage

### Basic Usage

**Transcribe a local audio file:**
```bash
python main.py audio.wav --models whisper
```

**Transcribe a YouTube video:**
```bash
python main.py "https://www.youtube.com/watch?v=your_video_id" --models whisper parakeet
```

**Use multiple models with consensus:**
```bash
python main.py audio.mp3 --models whisper parakeet canary
```

**Custom output directory:**
```bash
python main.py audio.wav --models whisper --output-dir ./results
```

**Skip consensus creation:**
```bash
python main.py audio.wav --models whisper parakeet --no-consensus
```

**Verbose output for debugging:**
```bash
python main.py audio.wav --models whisper --verbose
```

### Command Line Options

```
usage: main.py [-h] [--models MODELS [MODELS ...]] [--config CONFIG] 
               [--output-dir OUTPUT_DIR] [--no-consensus] [--verbose] 
               [--version] input

positional arguments:
  input                 Path to a local audio/video file or a YouTube URL.

options:
  -h, --help            show this help message and exit
  --models MODELS [MODELS ...]
                        Transcription models to use
  --config CONFIG       Path to a config file (default: config.yaml)
  --output-dir OUTPUT_DIR
                        Base output directory (default: output)
  --no-consensus        Skip creating consensus when multiple models are used
  --verbose, -v         Enable verbose output
  --version             show program's version number and exit
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
  parakeet:
    model_name: "nvidia/parakeet-tdt-0.6b-v3"
    device: "cuda"
  canary:
    model_name: "nvidia/canary-1b"
    device: "cuda"
```

### Available Models

- **whisper**: OpenAI's Whisper model with various size options (tiny, base, small, medium, large, large-v2, large-v3)
- **parakeet**: NVIDIA's TDT based ASR model, optimized for streaming applications
- **canary**: NVIDIA's multilingual ASR model supporting multiple languages

### Output Formats

The tool can generate transcripts in multiple formats:
- **JSON**: Detailed format with segments and timestamps
- **SRT**: Standard subtitle format
- **CSV**: Comma-separated values for data analysis

## Advanced Features

### Consensus Algorithm

When using multiple models, flersucker creates a consensus transcription using an advanced word-level voting algorithm:

1. **Word-level Analysis**: Each word position is analyzed across all transcriptions
2. **Similarity Scoring**: Transcriptions are compared for overall similarity
3. **Majority Voting**: The most common word at each position is selected
4. **Fallback Strategy**: If consensus fails, the best overall transcription is used

### Error Handling

The refactored codebase includes comprehensive error handling:

- **Custom Exceptions**: Specific exception types for different error scenarios
- **Graceful Degradation**: Failed models don't prevent others from running
- **Detailed Logging**: Verbose mode provides detailed error information
- **Fallback Mechanisms**: Backup strategies when primary methods fail

### Type Safety

The entire codebase uses Python type hints for:

- **Better IDE Support**: Improved autocomplete and error detection
- **Code Documentation**: Types serve as inline documentation
- **Runtime Validation**: Can be used with tools like mypy for static analysis
- **Maintainability**: Easier to understand and modify code

## Development

### Code Structure

The refactored architecture follows these principles:

- **Single Responsibility**: Each module has a clear, focused purpose
- **Open/Closed Principle**: Easy to extend with new models without modifying existing code
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Interface Segregation**: Clean, minimal interfaces between components

### Adding New Models

To add a new transcription model:

1. Create a new file in `src/models/` (e.g., `model_newmodel.py`)
2. Inherit from `BaseTranscriptionModel`
3. Implement the required abstract methods
4. Add configuration options to `config.py`
5. Update the available models list

Example:

```python
from .base import BaseTranscriptionModel

class NewModel(BaseTranscriptionModel):
    def load_model(self):
        # Load your model here
        pass
    
    def transcribe_audio(self, input_file: str) -> str:
        # Implement transcription logic
        pass
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes following the established patterns
4. Add tests if applicable
5. Submit a pull request

The codebase prioritizes:
- **Simplicity**: Clear, readable code over clever solutions
- **Elegance**: Pythonic patterns and clean interfaces
- **Maintainability**: Modular design and comprehensive documentation
- **Reliability**: Robust error handling and graceful degradation

## License

This project is open source. Please check the license file for details.