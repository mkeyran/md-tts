"""
Tests for TTS service.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.tts_service import TTSService


class TestTTSService:
    """Test cases for TTSService."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = TTSService(storage_path=self.temp_dir)
    
    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directories(self) -> None:
        """Test that initialization creates required directories."""
        assert self.service.storage_path.exists()
        assert self.service.audio_path.exists()
        assert self.service.storage_path == Path(self.temp_dir)
        assert self.service.audio_path == Path(self.temp_dir) / "audio"
    
    def test_cuda_detection(self) -> None:
        """Test CUDA detection."""
        cuda_info = self.service.get_cuda_info()
        
        assert "cuda_available" in cuda_info
        assert "cuda_version" in cuda_info
        assert "device_count" in cuda_info
        assert "device_name" in cuda_info
        
        # Should be boolean
        assert isinstance(cuda_info["cuda_available"], bool)
    
    @patch('services.tts_service.PiperVoice')
    @patch('services.tts_service.asyncio.create_subprocess_exec')
    async def test_initialize_voice_success(self, mock_subprocess, mock_piper_voice) -> None:
        """Test successful voice initialization."""
        # Mock successful download
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"success", b""))
        mock_subprocess.return_value = mock_process
        
        # Mock PiperVoice.load
        mock_voice = Mock()
        mock_piper_voice.load.return_value = mock_voice
        
        # Create mock model files
        models_dir = Path(self.temp_dir) / "models"
        models_dir.mkdir(exist_ok=True)
        (models_dir / "en_US-lessac-medium.onnx").touch()
        (models_dir / "en_US-lessac-medium.onnx.json").touch()
        
        await self.service.initialize_voice()
        
        assert self.service.voice == mock_voice
        mock_piper_voice.load.assert_called_once_with(
            models_dir / "en_US-lessac-medium.onnx",
            use_cuda=self.service.cuda_available
        )
    
    async def test_download_voice_model_failure(self) -> None:
        """Test voice model download failure."""
        # Test with unsupported voice model
        with pytest.raises(RuntimeError, match="Voice model .* not supported"):
            await self.service._download_voice_model("unsupported-voice")
    
    async def test_download_voice_model_existing_files(self) -> None:
        """Test that existing model files are reused."""
        models_dir = Path(self.temp_dir) / "models"
        models_dir.mkdir(exist_ok=True)
        
        model_file = models_dir / "test-voice.onnx"
        config_file = models_dir / "test-voice.onnx.json"
        model_file.touch()
        config_file.touch()
        
        result = await self.service._download_voice_model("test-voice")
        
        assert result == model_file
        assert model_file.exists()
        assert config_file.exists()
    
    @patch.object(TTSService, 'initialize_voice')
    @patch.object(TTSService, '_convert_to_mp3')
    @patch('wave.open')
    async def test_convert_text_to_speech_success(self, mock_wave_open, mock_convert_mp3, mock_init_voice) -> None:
        """Test successful text-to-speech conversion."""
        # Mock voice
        mock_voice = Mock()
        
        # Mock wave file
        mock_wav_file = Mock()
        mock_wav_file.__enter__ = Mock(return_value=mock_wav_file)
        mock_wav_file.__exit__ = Mock(return_value=None)
        mock_wave_open.return_value = mock_wav_file
        
        # Setup voice synthesize to create a dummy file
        def mock_synthesize(text, wav_file):
            # Just create a dummy file at the expected location
            # The convert_text_to_speech method will create the file path
            pass
        
        # Override wave.open to create actual files
        def mock_wave_open_func(filename, mode):
            # Create a dummy file
            Path(filename).touch()
            return mock_wav_file
        
        mock_wave_open.side_effect = mock_wave_open_func
        mock_voice.synthesize = Mock(side_effect=mock_synthesize)
        self.service.voice = mock_voice
        
        # Mock MP3 conversion
        mock_convert_mp3.return_value = None
        
        text = "Hello, this is a test."
        title = "Test Conversion"
        
        conversion_id, audio_file = await self.service.convert_text_to_speech(text, title)
        
        # Check that conversion ID is valid UUID format
        assert len(conversion_id) == 36
        assert "-" in conversion_id
        
        # Check file path
        assert audio_file.parent == self.service.audio_path
        assert audio_file.suffix == ".mp3"
        assert title.replace(" ", "_") in str(audio_file) or "Test" in str(audio_file)
        
        # Voice should have been called with text and a wave file
        assert mock_voice.synthesize.call_count == 1
        call_args = mock_voice.synthesize.call_args[0]
        assert call_args[0] == text
        # Check that wave.open was called
        mock_wave_open.assert_called_once()
        
        # MP3 conversion should have been called
        mock_convert_mp3.assert_called_once()
    
    @patch.object(TTSService, 'initialize_voice')
    @patch('wave.open')
    async def test_convert_text_to_speech_no_title(self, mock_wave_open, mock_init_voice) -> None:
        """Test text-to-speech conversion without title."""
        # Mock voice
        mock_voice = Mock()
        
        # Mock wave file
        mock_wav_file = Mock()
        mock_wav_file.__enter__ = Mock(return_value=mock_wav_file)
        mock_wav_file.__exit__ = Mock(return_value=None)
        mock_wave_open.return_value = mock_wav_file
        
        # Override wave.open to create actual files
        def mock_wave_open_func(filename, mode):
            # Create a dummy file
            Path(filename).touch()
            return mock_wav_file
        
        mock_wave_open.side_effect = mock_wave_open_func
        mock_voice.synthesize = Mock()
        self.service.voice = mock_voice
        
        text = "Hello, this is a test."
        
        with patch.object(self.service, '_convert_to_mp3', return_value=None):
            conversion_id, audio_file = await self.service.convert_text_to_speech(text)
        
        # Check that filename contains conversion ID
        assert conversion_id in str(audio_file)
        # Without title, filename should just be {conversion_id}.mp3
        filename = audio_file.name
        assert filename.startswith(conversion_id)
        assert filename.endswith('.mp3')
        # Should not have title-related underscores (UUIDs have dashes, which is fine)
        parts = filename.replace('.mp3', '').split('_')
        assert len(parts) == 1  # Only the UUID part
    
    @patch('services.tts_service.asyncio.create_subprocess_exec')
    async def test_convert_to_mp3_success(self, mock_subprocess) -> None:
        """Test successful WAV to MP3 conversion."""
        # Mock successful ffmpeg
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"", b""))
        mock_subprocess.return_value = mock_process
        
        wav_file = Path(self.temp_dir) / "test.wav"
        mp3_file = Path(self.temp_dir) / "test.mp3"
        wav_file.touch()
        
        await self.service._convert_to_mp3(wav_file, mp3_file)
        
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0]
        assert "ffmpeg" in args
        assert str(wav_file) in args
        assert str(mp3_file) in args
    
    @patch('services.tts_service.asyncio.create_subprocess_exec')
    async def test_convert_to_mp3_ffmpeg_not_found(self, mock_subprocess) -> None:
        """Test MP3 conversion when ffmpeg is not available."""
        # Mock FileNotFoundError (ffmpeg not found)
        mock_subprocess.side_effect = FileNotFoundError("ffmpeg not found")
        
        wav_file = Path(self.temp_dir) / "test.wav"
        mp3_file = Path(self.temp_dir) / "test.mp3"
        wav_file.touch()
        
        await self.service._convert_to_mp3(wav_file, mp3_file)
        
        # WAV file should be renamed to have .wav extension (since ffmpeg not found)
        expected_file = mp3_file.with_suffix('.wav')
        assert expected_file.exists()
        assert not wav_file.exists() or wav_file == expected_file
    
    def test_get_audio_file_path_exists(self) -> None:
        """Test getting audio file path when file exists."""
        conversion_id = "test-123"
        audio_file = self.service.audio_path / f"{conversion_id}.mp3"
        audio_file.touch()
        
        result = self.service.get_audio_file_path(conversion_id)
        
        assert result == audio_file
    
    def test_get_audio_file_path_not_exists(self) -> None:
        """Test getting audio file path when file doesn't exist."""
        result = self.service.get_audio_file_path("nonexistent")
        
        assert result is None
    
    def test_get_file_size(self) -> None:
        """Test getting file size."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "Hello, world!"
        test_file.write_text(test_content)
        
        size = self.service.get_file_size(test_file)
        
        assert size == len(test_content)
    
    def test_get_file_size_nonexistent(self) -> None:
        """Test getting file size for nonexistent file."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.txt"
        
        size = self.service.get_file_size(nonexistent_file)
        
        assert size == 0
    
    def test_cleanup_old_files(self) -> None:
        """Test cleanup of old audio files."""
        import time
        import os
        
        # Create old file
        old_file = self.service.audio_path / "old.mp3"
        old_file.touch()
        
        # Make it old by modifying timestamp
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        os.utime(old_file, (old_time, old_time))
        
        # Create new file
        new_file = self.service.audio_path / "new.mp3"
        new_file.touch()
        
        # Run cleanup with 7 day threshold
        self.service.cleanup_old_files(max_age_days=7)
        
        # Old file should be deleted, new file should remain
        assert not old_file.exists()
        assert new_file.exists()


