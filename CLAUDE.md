# Claude Code Instructions

This file contains instructions for Claude Code when working on this project.

## Project Overview

This is a TTS (Text-to-Speech) web application that converts markdown documents to audio files using piper-tts.

## Development Commands

### Package Management
- `uv sync` - Install/update dependencies
- `uv add <package>` - Add new dependency
- `uv run <command>` - Run command in project environment

### Running the Application
- `uv run uvicorn main:app --reload` - Start development server
- `uv run uvicorn main:app --host 0.0.0.0 --port 8000` - Start production server

### Testing
- `uv run pytest` - Run all tests
- `uv run pytest -v` - Run tests with verbose output
- `uv run pytest tests/` - Run specific test directory
- `uv run pytest --cov` - Run tests with coverage

### Code Quality
- `uv run ruff check` - Run linting
- `uv run ruff format` - Format code
- `uv run mypy .` - Type checking

## Project Structure

- `main.py` - FastAPI application entry point
- `models/` - Pydantic models and database schemas
- `services/` - Business logic and external integrations
- `static/` - Frontend HTML/CSS/JavaScript files
- `storage/` - File storage for MP3 files and database
- `tests/` - Test files organized by module

## Technology Notes

- Uses FastAPI for the web framework
- piper-tts for text-to-speech conversion
- SQLite for storing conversion history
- Vanilla JavaScript for frontend (no React)
- uv for package management instead of pip/poetry