import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from datetime import datetime, timedelta

from playlist.models import Playlist, Track


class ImportSpotifyPlaylistByUrl:
    """Importing a spotify's playlist by url, then saving into db

    Args:
        playlist_url (`str`): An url of a playlist.
        user(`User model instance`): Current user instance.
    """
    def __init__(self, playlist_url, user, request) -> None:
        self.playlist_url = playlist_url
        self.user = user
        self.auth_manager = SpotifyClientCredentials(
            client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
            cache_handler=spotipy.cache_handler.DjangoSessionCacheHandler(request=request)
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_playlist_tracks(self, playlist_id):
        """Playlist's tracks

        Args:
            playlist_id: playlist id

        Returns:
            json of the playlist's tracks
        """
        results = self.sp.playlist_tracks(playlist_id)
        tracks = results["items"]
        while results["next"]:
            results = self.sp.next(results)
            tracks.extend(results["items"])
        return tracks

    def get_spotify_playlist_by_url(self):
        """Get full information about playlist by it url and save it to a DB."""
        playlist_id = self.playlist_url.split("/")[-1]

        if "?" in playlist_id:
            playlist_id = playlist_id.split("?")[0]

        results = self.sp.playlist(playlist_id)
        playlist_name = results['name']
        owner_name = results['owner']['display_name']
        img_cover = results['images'][0]['url']
        tracks = self.get_playlist_tracks(playlist_id)

        self.save_playlist_into_db(
            playlist_name=playlist_name,
            owner_name=owner_name,
            img_cover=img_cover,
            tracks=tracks,
        )

    def save_playlist_into_db(self, playlist_name, owner_name, tracks, img_cover):
        """Save playlist and tracks into db"""
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

            new_track = Track(
                playlist=new_playlist,
                artist=track["track"]["artists"][0]["name"],
                track_name=track["track"]["name"],
                duration=duration,
                img_cover_url=track["track"]["album"]["images"][0]["url"],
            )
            track_list.append(new_track)

        Track.objects.bulk_create(track_list)


class SpotifyAuth:
    def __init__(self, request, user_id) -> None:
        self.auth_manager = SpotifyOAuth(
            client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
            client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
            cache_handler=spotipy.cache_handler.DjangoSessionCacheHandler(request),
            redirect_uri=f"http://localhost:8000/user/profile/{user_id}",
            scope="""user-library-read,
                playlist-read-private,
                playlist-modify-private,
                playlist-modify-public,
                user-read-private,
                user-library-modify,
                user-library-read""",
            show_dialog=True,
            open_browser=False,
        ),


class SyncPlaylists:
    def __init__(self, request, user_id, playlist_ids, public_playlist):
        self.auth_manager = SpotifyAuth(request, user_id),
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager),

        self.playlist_ids = playlist_ids,
        self.is_public_playlist = public_playlist,

    def sync_playlists(self):
        for playlist_id in self.playlist_ids:
            print(playlist_id)
