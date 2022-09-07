from datetime import datetime, timedelta
from yandex_music import Client

from ya_music.collage_maker import CollageMaker

from playlist.models import Playlist, Track


class ImportYandexMusicPlaylistByUrl:
    def __init__(self, playlist_url, user) -> None:
        self.playlist_url = playlist_url
        self.user = user

    def get_yandex_playlist_by_url(self):
        username = self.playlist_url.split("/")[4]
        kind_playlist = self.playlist_url.split("/")[-1]
        playlist = Client().users_playlists(int(kind_playlist), username)
        playlist_name = playlist.title
        owner_name = playlist.owner["name"]
        tracks = playlist.tracks

        if playlist.cover["uri"] is None:
            collage_maker = CollageMaker(self.user)
            img_cover_url = collage_maker.cover_processing(
                playlist=playlist, username=username, kind_playlist=kind_playlist
            )
        else:
            img_cover_url = str(playlist.cover["uri"]).replace("%%", "200x200")
            img_cover_url = f"https://{img_cover_url}"

        self.save_playlist_into_db(
            playlist_name=playlist_name,
            owner_name=owner_name,
            img_cover=img_cover_url,
            tracks=tracks,
        )

    def save_playlist_into_db(self, playlist_name, owner_name, tracks, img_cover):
        """Save playlist and tracks into db"""
        print(img_cover)
        new_playlist = Playlist(
            user=self.user,
            playlist_name=playlist_name,
            owner_name=owner_name,
            img_cover_url=img_cover,
        )
        new_playlist.save()

        track_list = []

        for track in tracks:
            duration_ms = int(track["track"]["duration_ms"])
            duration_and_random_date = datetime(1970, 1, 1) + timedelta(
                milliseconds=duration_ms
            )
            duration = duration_and_random_date.strftime("%M:%S")

            img_cover_url = str(track["track"]["cover_uri"]).replace("%%", "200x200")
            img_cover_url = f"https://{img_cover_url}"

            new_track = Track(
                playlist=new_playlist,
                artist=track["track"]["artists"][0]["name"],
                track_name=track["track"]["title"],
                duration=duration,
                img_cover_url=img_cover_url,
            )
            track_list.append(new_track)

        Track.objects.bulk_create(track_list)
