"""
FastAPI application for TTS Markdown Converter.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="TTS Markdown Converter",
    description="Convert markdown documents to speech using piper-tts",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint returning basic info."""
    return {"message": "TTS Markdown Converter API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}