from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from music_processing_api import routers


app = FastAPI(
    title='Music Metadata Processing API'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(routers.router)
