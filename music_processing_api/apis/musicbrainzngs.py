import musicbrainzngs
from fastapi import HTTPException, status

from music_processing_api.dbs.postgres import postgres
from music_processing_api.utils.date import milliseconds_to_time

musicbrainzngs.set_useragent("MyApp", "1.0", "your_email@example.com")

class RecordingInfo:
    song_title = None
    artist_name = None
    album_name = None
    length = None
    release_type = None

    def get_song_info(self):
        return {
            'song_title': self.song_title,
            'artist_name': self.artist_name,
            'album_name': self.album_name,
            'length': self.length
        }

class SongData:
    page_size = 25

    def __init__(self, song_title, artist_name):
        self.song_title = song_title
        self.artist_name = artist_name

    def search_result_gen(self):
        skip_size = 0
        while True:
            search_result = musicbrainzngs.search_recordings(
                recording=self.song_title,
                artist=self.artist_name,
                limit=self.page_size,
                offset=skip_size
            )
            recordings = search_result.get('recording-list')
            if not recordings:
                break
            yield recordings
            skip_size += self.page_size

    def get_recording_info(self, recording: dict):
        recording_title = recording.get('title')
        recording_length = recording.get('length')

        artist_data_list = recording.get('artist-credit', [{}])
        artist_data = artist_data_list[0]
        recording_artist_name = artist_data.get('name') if isinstance(artist_data, dict) else None

        release_list_data = recording.get('release-list', [{}])
        release_data = release_list_data[0].get('release-group', {})

        recording_release_type = release_data.get('type')
        recording_release_title = release_data.get('title')

        recording_info = RecordingInfo()

        recording_info.song_title = recording_title
        recording_info.artist_name = recording_artist_name
        recording_info.release_type = recording_release_type
        recording_info.album_name = recording_release_title
        recording_info.length = milliseconds_to_time(int(recording_length)) if recording_length is not None else None

        return recording_info

    @postgres.insert_to_db()
    def get_song_info(self):
        for recordings in self.search_result_gen():
            for recording in recordings:

                recording_info = self.get_recording_info(recording)

                if (
                        not recording_info.song_title
                        or not recording_info.artist_name
                        or recording_info.song_title.lower() != self.song_title.lower()
                        or recording_info.artist_name.lower() != self.artist_name.lower()
                ):
                    return recording_info.get_song_info()

                if not recording_info.length or recording_info.release_type != 'Album':
                    continue

                return recording_info.get_song_info()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Song \'{self.song_title}\' of \'{self.artist_name}\' artist was not found')
