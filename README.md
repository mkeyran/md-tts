# TTS Markdown Converter

A web-based text-to-speech application that converts markdown documents to audio files using piper-tts.

## Features

- Simple web interface for pasting markdown text
- Text-to-speech conversion using piper-tts with CUDA acceleration
- MP3 file generation and download
- Conversion history tracking
- Responsive web UI

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **TTS**: piper-tts with CUDA support
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Package Management**: uv
- **Testing**: pytest
- **Storage**: SQLite for history, local filesystem for MP3 files

## Development

This project uses `uv` for package management.

### Setup

```bash
# Install Python 3.11 (required for piper-tts)
uv python install 3.11

# Install dependencies
uv sync --dev --python 3.11

# Run the application
uv run uvicorn main:app --reload

# Run tests
uv run pytest

# Code quality checks
uv run ruff check
uv run ruff format
uv run mypy .
```

## Usage

1. Start the server
2. Open your browser to the web interface
3. Paste your markdown text
4. Click "Convert to Speech"
5. Download the generated MP3 file

## Project Structure

```
tts/
├── main.py                      # FastAPI application entry point
├── models/
│   └── schemas.py              # Pydantic request/response models
├── services/
│   ├── markdown_processor.py  # Markdown text extraction
│   └── tts_service.py          # TTS conversion with piper-tts
├── static/                     # Frontend HTML/CSS/JavaScript
├── storage/                    # MP3 files and SQLite database
├── tests/                      # Test files
│   └── test_*.py              # Test modules
└── pyproject.toml             # Project configuration
```

## Current Status

- ✅ Project setup with uv and FastAPI
- ✅ Markdown processing and text extraction
- ⏳ Piper-TTS integration (in progress)
- ⏳ File storage and download endpoints
- ⏳ Conversion history tracking
- ⏳ Web frontend interface