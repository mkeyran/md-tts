"""
FastAPI application for TTS Markdown Converter.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models.schemas import ConvertRequest, ConvertResponse, HistoryResponse, VoicesResponse, VoiceModelInfo
from models.voice_models import get_available_voices, get_default_voice
from services.database_service import DatabaseService
from services.markdown_processor import MarkdownProcessor
from services.tts_service import TTSService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
tts_service: TTSService = None
markdown_processor: MarkdownProcessor = None
db_service: DatabaseService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global tts_service, markdown_processor, db_service

    # Startup
    logger.info("Starting TTS Markdown Converter...")

    # Initialize services
    tts_service = TTSService()
    markdown_processor = MarkdownProcessor()
    db_service = DatabaseService()

    # Initialize TTS voice model
    try:
        await tts_service.initialize_voice()
        logger.info("TTS service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize TTS service: {e}")
        # Continue anyway - will try to initialize on first use

    yield

    # Shutdown
    logger.info("Shutting down TTS Markdown Converter...")


app = FastAPI(
    title="TTS Markdown Converter",
    description="Convert markdown documents to speech using piper-tts",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files
static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main web interface."""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "TTS Markdown Converter API", "version": "0.1.0"}


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {"message": "TTS Markdown Converter API", "version": "0.1.0"}


@app.get("/voices", response_model=VoicesResponse)
async def get_available_voices_endpoint():
    """Get list of available voice models."""
    try:
        voices = get_available_voices()
        default_voice = get_default_voice()
        
        voice_list = [
            VoiceModelInfo(
                id=voice.id,
                language=voice.language,
                language_code=voice.language_code,
                language_name=voice.language_name,
                speaker=voice.speaker,
                quality=voice.quality,
                gender=voice.gender,
                description=voice.description
            )
            for voice in voices
        ]
        
        return VoicesResponse(
            voices=voice_list,
            default_voice=default_voice.id
        )
    
    except Exception as e:
        logger.error(f"Failed to get available voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve voice models")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    cuda_info = (
        tts_service.get_cuda_info() if tts_service else {"cuda_available": False}
    )
    return {
        "status": "healthy",
        "services": {
            "tts": "ready" if tts_service and tts_service.voice else "initializing",
            "markdown": "ready" if markdown_processor else "error",
        },
        "cuda": cuda_info,
    }


@app.post("/convert", response_model=ConvertResponse)
async def convert_markdown_to_speech(
    request: ConvertRequest, background_tasks: BackgroundTasks
):
    """Convert markdown text to speech."""
    conversion_id = None
    try:
        # Extract text from markdown
        text = markdown_processor.extract_text(request.markdown_text)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in markdown")

        # Convert to speech using specified voice
        conversion_id, audio_file = await tts_service.convert_text_to_speech(
            text, request.title, request.voice_id
        )

        # Record conversion in database
        try:
            db_service.create_conversion_record(
                conversion_id=conversion_id,
                markdown_text=request.markdown_text,
                title=request.title,
            )

            # Update with success details
            file_size = tts_service.get_file_size(audio_file)
            db_service.update_conversion_success(
                conversion_id=conversion_id,
                file_path=str(audio_file),
                file_size=file_size,
            )
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            # Continue anyway - conversion succeeded

        # Schedule cleanup of old files
        background_tasks.add_task(tts_service.cleanup_old_files)
        background_tasks.add_task(db_service.cleanup_old_records)

        download_url = f"/download/{conversion_id}"

        return ConvertResponse(
            conversion_id=conversion_id,
            status="completed",
            message="Conversion successful",
            download_url=download_url,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {e}")

        # Record failure in database if we have a conversion_id
        if conversion_id:
            try:
                db_service.update_conversion_failed(conversion_id, str(e))
            except Exception as db_error:
                logger.error(f"Database error recording failure: {db_error}")

        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.get("/download/{conversion_id}")
async def download_audio_file(conversion_id: str):
    """Download the generated audio file."""
    try:
        audio_file = tts_service.get_audio_file_path(conversion_id)

        if not audio_file or not audio_file.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Determine media type
        media_type = "audio/mpeg" if audio_file.suffix == ".mp3" else "audio/wav"

        return FileResponse(
            path=audio_file, media_type=media_type, filename=audio_file.name
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail="Download failed")


@app.get("/status/{conversion_id}")
async def get_conversion_status(conversion_id: str):
    """Get the status of a conversion."""
    try:
        audio_file = tts_service.get_audio_file_path(conversion_id)

        if audio_file and audio_file.exists():
            file_size = tts_service.get_file_size(audio_file)
            return {
                "conversion_id": conversion_id,
                "status": "completed",
                "file_size": file_size,
                "download_url": f"/download/{conversion_id}",
            }
        else:
            return {
                "conversion_id": conversion_id,
                "status": "not_found",
                "message": "Conversion not found or expired",
            }

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "conversion_id": conversion_id,
            "status": "error",
            "message": "Status check failed",
        }


@app.get("/history", response_model=HistoryResponse)
async def get_conversion_history(limit: int = 50, offset: int = 0):
    """Get conversion history."""
    try:
        if limit > 100:
            limit = 100  # Prevent excessive queries

        return db_service.get_conversion_history(limit=limit, offset=offset)

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@app.delete("/history/{conversion_id}")
async def delete_conversion_history(conversion_id: str):
    """Delete a conversion from history."""
    try:
        # Delete from database
        deleted = db_service.delete_conversion_record(conversion_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Conversion not found")

        # Also try to delete the audio file
        audio_file = tts_service.get_audio_file_path(conversion_id)
        if audio_file and audio_file.exists():
            try:
                audio_file.unlink()
                logger.info(f"Deleted audio file: {audio_file}")
            except Exception as file_error:
                logger.warning(f"Could not delete audio file: {file_error}")

        return {"message": "Conversion deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversion")
