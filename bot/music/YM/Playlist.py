from .import client
from .Track import Track
from typing import List
from yandex_music import Track as track_object_

class Playlist:
    """Плейлист"""


    def __init__(self, user_id: str, playlist_id: int, album_id: int = None, track_id: int = None,) -> None:
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.tracks: List[Track] = []
        self.title: str
        self.preview: str
        self.album_id = album_id
        self.track_id = track_id

    
    async def fetch_playlist(self):
        playlist = await client.users_playlists(kind=self.playlist_id, user_id=self.user_id)

        self.title = self.user_id if not playlist.title else playlist.title
        self.preview = "https://" + playlist.og_image.replace("%%", "1000x1000")
        
        for track in playlist.tracks:
            self.tracks.append(await Track(track_object=track).fetch_track())

        return self

    async def find_similar_tracks(self):
        similar = await client.tracksSimilar(f"{self.user_id}:{self.playlist_id}")

        similar_tracks = []  # Создаем новый список для похожих треков
        if len(similar.similar_tracks) != 0:
            for track_data in similar.similar_tracks:
                similar_tracks.append(await Track(track_object=track_data).fetch_track())

            # Создаем новый объект Playlist и добавляем в него треки
            similar_playlist = Playlist(user_id="test",
                                        playlist_id=-1)
            similar_playlist.title = f"Похожие треки на {similar.track.title}"
            similar_playlist.tracks = similar_tracks
            return similar_playlist
        else:
            return None


