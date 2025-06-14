# Claude Code Instructions

This file contains instructions for Claude Code when working on this project.

## Project Overview

This is a TTS (Text-to-Speech) web application that converts markdown documents to audio files using piper-tts.

## Development Commands

### Package Management
- `uv python install 3.11` - Install Python 3.11 (required for piper-tts)
- `uv sync --dev --python 3.11` - Install/update dependencies with Python 3.11
- `uv add <package>` - Add new dependency
- `uv run <command>` - Run command in project environment

### Running the Application

**Local Development:**
- `uv run uvicorn main:app --reload` - Start development server
- `uv run uvicorn main:app --host 0.0.0.0 --port 8000` - Start production server

**Docker (Recommended for Production):**
- `docker-compose up tts-cpu` - Run CPU version on port 8000
- `docker-compose up tts-cuda` - Run CUDA version on port 8001 (requires nvidia-docker)
- `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up tts-cpu` - Development mode with hot reload
- `docker-compose up -d tts-cpu` - Run in background
- `docker-compose logs -f tts-cpu` - View logs
- `docker-compose down` - Stop services

### Testing
- `uv run pytest` - Run all tests (58 tests)
- `uv run pytest -v` - Run tests with verbose output
- `uv run pytest tests/` - Run specific test directory
- `uv run pytest --cov` - Run tests with coverage
- `uv run pytest tests/test_main.py` - Run API endpoint tests
- `uv run pytest tests/test_tts_service.py` - Run TTS service tests
- `uv run pytest tests/test_markdown_processor.py` - Run markdown processor tests
- `uv run pytest tests/test_database_service.py` - Run database service tests

### Code Quality
- `uv run ruff check` - Run linting
- `uv run ruff format` - Format code
- `uv run mypy .` - Type checking

## Project Structure

- `main.py` - FastAPI application entry point
- `models/` - Pydantic models and database schemas
- `services/` - Business logic and external integrations
- `static/` - Frontend HTML/CSS/JavaScript files
  - `index.html` - Main web interface with responsive design
  - `style.css` - Modern CSS styling with gradients and animations
  - `app.js` - Frontend application with automated status updates
- `storage/` - File storage for MP3 files and database
- `tests/` - Test files organized by module
- `Dockerfile.cpu` - Docker configuration for CPU-only deployment
- `Dockerfile.cuda` - Docker configuration for CUDA/GPU deployment
- `docker-compose.yml` - Docker Compose configuration
- `docker-compose.dev.yml` - Development Docker Compose override
- `.dockerignore` - Docker ignore patterns
- `requirements-cpu.txt` - CPU-only dependencies (no CUDA)
- `requirements-cuda.txt` - CUDA-enabled dependencies

## Technology Notes

- Uses FastAPI for the web framework with async support
- piper-tts for text-to-speech conversion (requires Python 3.8-3.11)
- Automatic voice model downloading from HuggingFace repositories
- CUDA acceleration support when available
- SQLite for storing conversion history
- Vanilla JavaScript for frontend (no React)
- uv for package management instead of pip/poetry
- Markdown library for parsing markdown documents
- BeautifulSoup for HTML text extraction
- aiohttp for async HTTP requests
- wave module for proper audio file handling

## Deployment Options

### Docker Deployment (Recommended)

**CPU Version:**
- Based on `python:3.11-slim` image
- Uses CPU-only PyTorch (no CUDA dependencies)
- Smaller image size, faster build times
- Suitable for development and light production use
- No GPU requirements
- Accessible on port 8000

**CUDA Version:**
- Based on `nvidia/cuda:12.1-runtime-ubuntu22.04` image
- Uses CUDA-enabled PyTorch with GPU acceleration
- Requires NVIDIA Container Toolkit
- Provides significant performance improvement for TTS conversion
- Accessible on port 8001
- Recommended for high-volume production use

**Key Features:**
- Optimized dependency installation (CPU vs CUDA variants)
- Health checks for monitoring
- Volume mounts for persistent storage
- Development mode with hot reload
- Proper cleanup and resource management
- Smaller CPU image without CUDA dependencies

## Development Progress

- ✅ Project structure and FastAPI setup
- ✅ Markdown processing with text extraction
- ✅ Comprehensive test suite for markdown processor
- ✅ Piper-TTS integration with CUDA detection
- ✅ Voice model auto-download from HuggingFace
- ✅ File storage and download endpoints
- ✅ Complete FastAPI backend with all endpoints
- ✅ 58 tests covering all functionality
- ✅ Conversion history database with SQLite
- ✅ Responsive web frontend with automated status updates
- ✅ Docker containerization with CPU and CUDA variants

## API Endpoints

### Implemented Endpoints
- `GET /` - Main web interface
- `GET /api` - API information and version
- `GET /health` - Health check with service status and CUDA info
- `POST /convert` - Convert markdown text to speech (returns conversion_id)
- `GET /download/{conversion_id}` - Download generated MP3 file
- `GET /status/{conversion_id}` - Check conversion status and file info
- `GET /history` - Get conversion history with pagination (limit/offset params)
- `DELETE /history/{conversion_id}` - Delete conversion from history and remove file

### Request/Response Examples

**Convert Text:**
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown_text": "# Hello\n\nThis is **test** text.", "title": "My Audio"}'
# Returns: {"conversion_id": "uuid", "status": "completed", "download_url": "/download/uuid"}
```

**Download Audio:**
```bash
curl -o audio.mp3 http://localhost:8000/download/{conversion_id}
```

**Check Status:**
```bash
curl http://localhost:8000/status/{conversion_id}
# Returns: {"conversion_id": "uuid", "status": "completed", "file_size": 12345, "download_url": "/download/uuid"}
```

**Get History:**
```bash
curl http://localhost:8000/history?limit=10&offset=0
# Returns: {"items": [{"id": "uuid", "title": "...", "text_preview": "...", "created_at": "...", "status": "completed", "file_size": 12345, "download_url": "/download/uuid"}]}
```

**Delete Conversion:**
```bash
curl -X DELETE http://localhost:8000/history/{conversion_id}
# Returns: {"message": "Conversion deleted successfully"}
```