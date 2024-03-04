from fastapi import APIRouter, FastAPI
from music_processing_api.routers import musicbrainzngs

router = APIRouter()

router.include_router(musicbrainzngs.router)