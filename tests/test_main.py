"""
Tests for FastAPI main application.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from httpx import AsyncClient

# Mock piper before importing main
sys.modules['piper'] = Mock()
sys.modules['piper.PiperVoice'] = Mock()

import main


class TestMainApplication:
    """Test cases for the main FastAPI application."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the global services
        main.tts_service = Mock()
        main.markdown_processor = Mock()
        
        # Create test client
        self.client = TestClient(main.app)
    
    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_root_endpoint(self) -> None:
        """Test the root endpoint."""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "TTS Markdown Converter API"
        assert data["version"] == "0.1.0"
    
    def test_health_check_ready(self) -> None:
        """Test health check when services are ready."""
        # Mock services as ready
        main.tts_service.voice = Mock()
        main.tts_service.get_cuda_info.return_value = {"cuda_available": True}
        
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["tts"] == "ready"
        assert data["services"]["markdown"] == "ready"
        assert data["cuda"]["cuda_available"] is True
    
    def test_health_check_initializing(self) -> None:
        """Test health check when TTS is initializing."""
        # Mock TTS as not ready
        main.tts_service.voice = None
        main.tts_service.get_cuda_info.return_value = {"cuda_available": False}
        
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["tts"] == "initializing"
        assert data["services"]["markdown"] == "ready"
    
    def test_convert_success(self) -> None:
        """Test successful markdown conversion."""
        # Mock successful processing
        main.markdown_processor.extract_text.return_value = "Hello, this is test text."
        main.tts_service.convert_text_to_speech = AsyncMock(
            return_value=("test-id-123", Path("test.mp3"))
        )
        main.tts_service.cleanup_old_files = Mock()
        
        request_data = {
            "markdown_text": "# Hello\n\nThis is test text.",
            "title": "Test Conversion"
        }
        
        response = self.client.post("/convert", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversion_id"] == "test-id-123"
        assert data["status"] == "completed"
        assert data["message"] == "Conversion successful"
        assert data["download_url"] == "/download/test-id-123"
        
        # Verify calls
        main.markdown_processor.extract_text.assert_called_once_with("# Hello\n\nThis is test text.")
        main.tts_service.convert_text_to_speech.assert_called_once_with(
            "Hello, this is test text.", "Test Conversion"
        )
    
    def test_convert_no_text_found(self) -> None:
        """Test conversion when no text is extracted."""
        # Mock empty text extraction
        main.markdown_processor.extract_text.return_value = ""
        
        request_data = {
            "markdown_text": "```python\nprint('code only')\n```"
        }
        
        response = self.client.post("/convert", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "No text found in markdown" in data["detail"]
    
    def test_convert_tts_failure(self) -> None:
        """Test conversion when TTS fails."""
        # Mock TTS failure
        main.markdown_processor.extract_text.return_value = "Test text"
        main.tts_service.convert_text_to_speech = AsyncMock(
            side_effect=Exception("TTS failed")
        )
        
        request_data = {
            "markdown_text": "# Test\n\nSome text."
        }
        
        response = self.client.post("/convert", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "Conversion failed" in data["detail"]
        assert "TTS failed" in data["detail"]
    
    def test_convert_invalid_request(self) -> None:
        """Test conversion with invalid request data."""
        # Missing required field
        request_data = {"title": "Test"}
        
        response = self.client.post("/convert", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_download_file_exists(self) -> None:
        """Test downloading an existing file."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.mp3"
        test_file.write_text("fake audio data")
        
        # Mock TTS service to return the test file
        main.tts_service.get_audio_file_path.return_value = test_file
        
        response = self.client.get("/download/test-id-123")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert "test.mp3" in response.headers.get("content-disposition", "")
        main.tts_service.get_audio_file_path.assert_called_once_with("test-id-123")
    
    def test_download_wav_file(self) -> None:
        """Test downloading a WAV file."""
        # Create a test WAV file
        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_text("fake audio data")
        
        # Mock TTS service to return the test file
        main.tts_service.get_audio_file_path.return_value = test_file
        
        response = self.client.get("/download/test-id-123")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
    
    def test_download_file_not_found(self) -> None:
        """Test downloading a non-existent file."""
        # Mock TTS service to return None
        main.tts_service.get_audio_file_path.return_value = None
        
        response = self.client.get("/download/nonexistent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "Audio file not found" in data["detail"]
    
    def test_download_file_missing(self) -> None:
        """Test downloading when file path exists but file is missing."""
        # Mock TTS service to return a non-existent file
        test_file = Path(self.temp_dir) / "missing.mp3"
        main.tts_service.get_audio_file_path.return_value = test_file
        
        response = self.client.get("/download/test-id-123")
        
        assert response.status_code == 404
        data = response.json()
        assert "Audio file not found" in data["detail"]
    
    def test_download_service_error(self) -> None:
        """Test download when service throws an error."""
        # Mock TTS service to raise exception
        main.tts_service.get_audio_file_path.side_effect = Exception("Service error")
        
        response = self.client.get("/download/test-id-123")
        
        assert response.status_code == 500
        data = response.json()
        assert "Download failed" in data["detail"]
    
    def test_status_file_exists(self) -> None:
        """Test status check for existing file."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.mp3"
        test_file.write_text("fake audio data")
        
        # Mock TTS service
        main.tts_service.get_audio_file_path.return_value = test_file
        main.tts_service.get_file_size.return_value = 1024
        
        response = self.client.get("/status/test-id-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversion_id"] == "test-id-123"
        assert data["status"] == "completed"
        assert data["file_size"] == 1024
        assert data["download_url"] == "/download/test-id-123"
    
    def test_status_file_not_found(self) -> None:
        """Test status check for non-existent file."""
        # Mock TTS service to return None
        main.tts_service.get_audio_file_path.return_value = None
        
        response = self.client.get("/status/nonexistent-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversion_id"] == "nonexistent-id"
        assert data["status"] == "not_found"
        assert "not found or expired" in data["message"]
    
    def test_status_service_error(self) -> None:
        """Test status check when service fails."""
        # Mock TTS service to raise exception
        main.tts_service.get_audio_file_path.side_effect = Exception("Service error")
        
        response = self.client.get("/status/test-id-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversion_id"] == "test-id-123"
        assert data["status"] == "error"
        assert "Status check failed" in data["message"]