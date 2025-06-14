# TTS Markdown Converter

A web-based text-to-speech application that converts markdown documents to audio files using piper-tts.

## Features

- 🎯 Simple web interface for pasting markdown text
- 🤖 Text-to-speech conversion using piper-tts with CUDA acceleration
- 📁 MP3 file generation and download
- 📊 Conversion history tracking
- 🎨 Responsive web UI
- 🚀 FastAPI backend with comprehensive endpoints
- 🧪 Complete test suite with 58 tests
- 📦 Automatic voice model downloading from HuggingFace

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **TTS**: piper-tts with CUDA support
- **Voice Models**: Auto-downloaded from HuggingFace
- **Frontend**: Vanilla HTML/CSS/JavaScript  
- **Package Management**: uv
- **Testing**: pytest with 58 comprehensive tests
- **Storage**: SQLite for history, local filesystem for MP3 files
- **Dependencies**: aiohttp, torch, markdown, beautifulsoup4

## Quick Start with Docker

### CPU Version
```bash
# Build and run CPU version
docker-compose up tts-cpu

# Access the application at http://localhost:8000
```

### CUDA Version (requires nvidia-docker)
```bash
# Build and run CUDA version
docker-compose up tts-cuda

# Access the application at http://localhost:8001
```

### Development Mode
```bash
# Run with hot reload for development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up tts-cpu
```

### Docker Requirements

**For CPU version:**
- Docker
- Docker Compose

**For CUDA version:**
- Docker
- Docker Compose
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- NVIDIA GPU with CUDA support

### Docker Commands

```bash
# Build images
docker-compose build

# Run in background
docker-compose up -d tts-cpu

# View logs
docker-compose logs -f tts-cpu

# Stop services
docker-compose down

# Clean up (remove containers and images)
docker-compose down --rmi all
```

## Local Development

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

1. Start the server: `uv run uvicorn main:app --reload`
2. Open your browser to http://localhost:8000
3. Paste your markdown text in the textarea
4. Optionally add a title for your audio file
5. Click "Convert to Speech" 
6. Wait for conversion to complete (automatic status updates)
7. Download the generated MP3 file
8. View and manage your conversion history

## Project Structure

```
tts/
├── main.py                      # FastAPI application entry point
├── models/
│   ├── schemas.py              # Pydantic request/response models
│   └── database.py             # SQLite database models
├── services/
│   ├── markdown_processor.py  # Markdown text extraction
│   ├── tts_service.py          # TTS conversion with piper-tts
│   └── database_service.py     # Conversion history management
├── static/                     # Frontend HTML/CSS/JavaScript
│   ├── index.html             # Main web interface
│   ├── style.css              # Responsive styling
│   └── app.js                 # Frontend application logic
├── storage/                    # MP3 files and SQLite database
├── tests/                      # Test files
│   └── test_*.py              # Test modules
├── Dockerfile.cpu             # Docker configuration for CPU
├── Dockerfile.cuda            # Docker configuration for CUDA/GPU
├── docker-compose.yml         # Docker Compose configuration
├── docker-compose.dev.yml     # Development Docker Compose override
├── .dockerignore              # Docker ignore patterns
└── pyproject.toml             # Project configuration
```

## API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `GET /api` - API information
- `GET /health` - Health check with service status and CUDA info
- `POST /convert` - Convert markdown text to speech
- `GET /download/{conversion_id}` - Download generated MP3 file
- `GET /status/{conversion_id}` - Check conversion status

### History Endpoints
- `GET /history` - Get conversion history with pagination
- `DELETE /history/{conversion_id}` - Delete conversion from history

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

# Get conversion history
curl http://localhost:8000/history

# Delete conversion from history
curl -X DELETE http://localhost:8000/history/{conversion_id}
```

## Current Status

- ✅ Project setup with uv and FastAPI
- ✅ Markdown processing and text extraction
- ✅ Piper-TTS integration with CUDA detection
- ✅ Voice model auto-download from HuggingFace
- ✅ File storage and download endpoints
- ✅ Complete API with MP3 generation
- ✅ Conversion history tracking with SQLite database
- ✅ Comprehensive test suite (58 tests)
- ✅ Responsive web frontend interface
- ✅ Docker containerization with CPU and CUDA variants