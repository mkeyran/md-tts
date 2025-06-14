# TTS Markdown Converter

A web-based text-to-speech application that converts markdown documents to audio files using piper-tts.

## Features

- 🎯 Simple web interface for pasting markdown text
- 🤖 Text-to-speech conversion using piper-tts with CUDA acceleration
- 📁 MP3 file generation and download
- 📊 Conversion history tracking
- 🎨 Responsive web UI
- 🚀 FastAPI backend with comprehensive endpoints
- 🧪 Complete test suite with 40+ tests
- 📦 Automatic voice model downloading from HuggingFace

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **TTS**: piper-tts with CUDA support
- **Voice Models**: Auto-downloaded from HuggingFace
- **Frontend**: Vanilla HTML/CSS/JavaScript  
- **Package Management**: uv
- **Testing**: pytest with 40+ comprehensive tests
- **Storage**: SQLite for history, local filesystem for MP3 files
- **Dependencies**: aiohttp, torch, markdown, beautifulsoup4

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

## API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check with service status and CUDA info
- `POST /convert` - Convert markdown text to speech
- `GET /download/{conversion_id}` - Download generated MP3 file
- `GET /status/{conversion_id}` - Check conversion status

### Example Usage

```bash
# Convert markdown to speech
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown_text": "# Hello\n\nThis is **test** text.", "title": "My Audio"}'

# Download the generated audio file
curl -o audio.mp3 http://localhost:8000/download/{conversion_id}

# Check conversion status
curl http://localhost:8000/status/{conversion_id}
```

## Current Status

- ✅ Project setup with uv and FastAPI
- ✅ Markdown processing and text extraction
- ✅ Piper-TTS integration with CUDA detection
- ✅ Voice model auto-download from HuggingFace
- ✅ File storage and download endpoints
- ✅ Complete API with MP3 generation
- ⏳ Conversion history tracking (in progress)
- ⏳ Web frontend interface