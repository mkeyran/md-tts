"""
FastAPI application for TTS Markdown Converter.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from models.schemas import ConvertRequest, ConvertResponse, HistoryResponse
from services.markdown_processor import MarkdownProcessor
from services.tts_service import TTSService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
tts_service: TTSService = None
markdown_processor: MarkdownProcessor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global tts_service, markdown_processor
    
    # Startup
    logger.info("Starting TTS Markdown Converter...")
    
    # Initialize services
    tts_service = TTSService()
    markdown_processor = MarkdownProcessor()
    
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
    lifespan=lifespan
)

# Mount static files
static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint returning basic info."""
    return {"message": "TTS Markdown Converter API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    cuda_info = tts_service.get_cuda_info() if tts_service else {"cuda_available": False}
    return {
        "status": "healthy",
        "services": {
            "tts": "ready" if tts_service and tts_service.voice else "initializing",
            "markdown": "ready" if markdown_processor else "error"
        },
        "cuda": cuda_info
    }


@app.post("/convert", response_model=ConvertResponse)
async def convert_markdown_to_speech(
    request: ConvertRequest,
    background_tasks: BackgroundTasks
):
    """Convert markdown text to speech."""
    try:
        # Extract text from markdown
        text = markdown_processor.extract_text(request.markdown_text)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in markdown")
        
        # Convert to speech
        conversion_id, audio_file = await tts_service.convert_text_to_speech(
            text, request.title
        )
        
        # Schedule cleanup of old files
        background_tasks.add_task(tts_service.cleanup_old_files)
        
        download_url = f"/download/{conversion_id}"
        
        return ConvertResponse(
            conversion_id=conversion_id,
            status="completed",
            message="Conversion successful",
            download_url=download_url
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
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
            path=audio_file,
            media_type=media_type,
            filename=audio_file.name
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
                "download_url": f"/download/{conversion_id}"
            }
        else:
            return {
                "conversion_id": conversion_id,
                "status": "not_found",
                "message": "Conversion not found or expired"
            }
            
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "conversion_id": conversion_id,
            "status": "error",
            "message": "Status check failed"
        }