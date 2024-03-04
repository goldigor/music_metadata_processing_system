from fastapi import APIRouter
from fastapi.responses import JSONResponse
from music_processing_api.apis.musicbrainzngs import SongData

router = APIRouter(
    prefix='/musicbrainzngs',
    tags=['musicbrainzngs']
)


@router.get('/imagine_dragons/search_song/{title}',
            tags=['musicbrainzngs'],
            response_class=JSONResponse)
async def search_song(title: str):
    data = SongData(song_title=title, artist_name='Imagine Dragons').get_song_info()
    return JSONResponse(data)
