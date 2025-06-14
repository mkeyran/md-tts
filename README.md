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
# Install dependencies
uv sync

# Run the application
uv run uvicorn main:app --reload

# Run tests
uv run pytest
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
├── main.py              # FastAPI application
├── models/              # Data models
├── services/            # Business logic
├── static/              # Frontend files
├── storage/             # File storage
├── tests/               # Test files
└── pyproject.toml       # Project configuration
```