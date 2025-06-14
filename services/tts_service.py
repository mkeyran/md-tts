"""
TTS service using piper-tts for text-to-speech conversion.
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Dict, Optional

import torch
from piper import PiperVoice

from models.voice_models import VoiceModel, get_voice_by_id, get_default_voice

logger = logging.getLogger(__name__)


class TTSService:
    """Service for text-to-speech conversion using piper-tts."""

    def __init__(self, storage_path: str = "storage") -> None:
        """
        Initialize TTS service.

        Args:
            storage_path: Directory to store generated audio files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Create audio subdirectory
        self.audio_path = self.storage_path / "audio"
        self.audio_path.mkdir(exist_ok=True)

        # Create models subdirectory
        self.models_path = self.storage_path / "models"
        self.models_path.mkdir(exist_ok=True)

        # Cache loaded voices
        self.loaded_voices: Dict[str, PiperVoice] = {}
        self.current_voice: Optional[PiperVoice] = None
        self.current_voice_id: Optional[str] = None
        self.cuda_available = torch.cuda.is_available()

        logger.info(f"TTS Service initialized. CUDA available: {self.cuda_available}")

    async def initialize_voice(self, voice_id: Optional[str] = None) -> None:
        """
        Initialize the piper voice model.

        Args:
            voice_id: Voice model ID to use for TTS
        """
        if voice_id is None:
            voice_id = get_default_voice().id
            
        try:
            # Load voice if not already loaded
            if voice_id not in self.loaded_voices:
                model_path = await self._download_voice_model(voice_id)
                voice = PiperVoice.load(model_path, use_cuda=self.cuda_available)
                self.loaded_voices[voice_id] = voice
                logger.info(f"Voice model loaded: {voice_id}")
            
            # Set current voice
            self.current_voice = self.loaded_voices[voice_id]
            self.current_voice_id = voice_id

        except Exception as e:
            logger.error(f"Failed to initialize voice model {voice_id}: {e}")
            raise

    async def get_voice(self, voice_id: Optional[str] = None) -> PiperVoice:
        """
        Get a voice model, loading it if necessary.

        Args:
            voice_id: Voice model ID

        Returns:
            Loaded PiperVoice instance
        """
        if voice_id is None:
            voice_id = get_default_voice().id

        if voice_id not in self.loaded_voices:
            await self.initialize_voice(voice_id)
        
        return self.loaded_voices[voice_id]

    @property
    def voice(self) -> Optional[PiperVoice]:
        """Get the current voice for backward compatibility."""
        return self.current_voice

    async def _download_voice_model(self, voice_id: str) -> Path:
        """
        Download voice model if it doesn't exist.

        Args:
            voice_id: Voice model ID

        Returns:
            Path to the voice model file
        """
        model_file = self.models_path / f"{voice_id}.onnx"
        config_file = self.models_path / f"{voice_id}.onnx.json"

        if model_file.exists() and config_file.exists():
            return model_file

        # Get voice model configuration
        voice_model = get_voice_by_id(voice_id)
        if not voice_model:
            raise RuntimeError(f"Voice model {voice_id} not found in configuration")

        # Download voice model from HuggingFace
        try:
            import aiohttp

            logger.info(f"Downloading voice model: {voice_id}")

            async with aiohttp.ClientSession() as session:
                # Download model file
                async with session.get(voice_model.model_url) as response:
                    if response.status == 200:
                        with open(model_file, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        logger.info(f"Downloaded model file: {model_file}")
                    else:
                        raise RuntimeError(
                            f"Failed to download model file: HTTP {response.status}"
                        )

                # Download config file
                async with session.get(voice_model.config_url) as response:
                    if response.status == 200:
                        with open(config_file, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        logger.info(f"Downloaded config file: {config_file}")
                    else:
                        raise RuntimeError(
                            f"Failed to download config file: HTTP {response.status}"
                        )

            logger.info(f"Successfully downloaded voice model: {voice_id}")
            return model_file

        except Exception as e:
            logger.error(f"Error downloading voice model: {e}")
            raise RuntimeError(f"Failed to download voice model: {e}")

    async def convert_text_to_speech(
        self, text: str, title: str | None = None, voice_id: str | None = None
    ) -> tuple[str, Path]:
        """
        Convert text to speech and save as audio file.

        Args:
            text: Text to convert to speech
            title: Optional title for the conversion
            voice_id: Voice model ID to use

        Returns:
            Tuple of (conversion_id, audio_file_path)
        """
        # Get the specified voice or default
        voice = await self.get_voice(voice_id)

        # Generate unique ID for this conversion
        conversion_id = str(uuid.uuid4())

        # Create filename
        filename = f"{conversion_id}.wav"
        if title:
            safe_title = "".join(
                c for c in title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            filename = f"{conversion_id}_{safe_title[:50]}.wav"

        audio_file = self.audio_path / filename

        try:
            # Generate audio using piper
            import wave

            with wave.open(str(audio_file), "wb") as wav_file:
                voice.synthesize(text, wav_file)

            logger.info(f"Generated audio file: {audio_file} using voice: {voice_id or 'default'}")

            # Convert to MP3 for better web compatibility
            mp3_file = audio_file.with_suffix(".mp3")
            await self._convert_to_mp3(audio_file, mp3_file)

            # Remove WAV file to save space
            audio_file.unlink()

            return conversion_id, mp3_file

        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            # Clean up on error
            if audio_file.exists():
                audio_file.unlink()
            raise

    async def _convert_to_mp3(self, wav_file: Path, mp3_file: Path) -> None:
        """
        Convert WAV file to MP3 using ffmpeg.

        Args:
            wav_file: Source WAV file
            mp3_file: Target MP3 file
        """
        try:
            cmd = [
                "ffmpeg",
                "-i",
                str(wav_file),
                "-acodec",
                "mp3",
                "-ab",
                "128k",
                "-y",
                str(mp3_file),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed: {stderr.decode()}")

        except FileNotFoundError:
            # FFmpeg not available, keep WAV file
            logger.warning("FFmpeg not found, keeping WAV file instead of MP3")
            wav_file.rename(mp3_file.with_suffix(".wav"))
        except Exception as e:
            logger.error(f"Error converting to MP3: {e}")
            # Fallback: rename WAV to MP3 extension (not ideal but works)
            wav_file.rename(mp3_file.with_suffix(".wav"))

    def get_audio_file_path(self, conversion_id: str) -> Path | None:
        """
        Get the path to an audio file by conversion ID.

        Args:
            conversion_id: Conversion ID

        Returns:
            Path to audio file if exists, None otherwise
        """
        # Check for both MP3 and WAV files
        for ext in [".mp3", ".wav"]:
            for file in self.audio_path.glob(f"{conversion_id}*{ext}"):
                if file.exists():
                    return file
        return None

    def get_file_size(self, file_path: Path) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            File size in bytes
        """
        return file_path.stat().st_size if file_path.exists() else 0

    def cleanup_old_files(self, max_age_days: int = 7) -> None:
        """
        Clean up old audio files.

        Args:
            max_age_days: Maximum age in days before deletion
        """
        import time

        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60

        for file in self.audio_path.iterdir():
            if file.is_file():
                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file.unlink()
                        logger.info(f"Deleted old audio file: {file}")
                    except Exception as e:
                        logger.error(f"Error deleting old file {file}: {e}")

    def get_cuda_info(self) -> dict:
        """
        Get CUDA information for diagnostics.

        Returns:
            Dictionary with CUDA information
        """
        return {
            "cuda_available": self.cuda_available,
            "cuda_version": torch.version.cuda if self.cuda_available else None,
            "device_count": torch.cuda.device_count() if self.cuda_available else 0,
            "device_name": torch.cuda.get_device_name(0)
            if self.cuda_available and torch.cuda.device_count() > 0
            else None,
        }
