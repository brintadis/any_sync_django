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
    def __init__(self, request) -> None:
        self.client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URL")
        self.request = request

    def spotipy_cache_handler(self):
        self.cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(self.request)

        return self.cache_handler

    def spotipy_auth_manager(self):
        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            cache_handler=self.spotipy_cache_handler(),
            redirect_uri=self.redirect_uri,
            scope="""user-library-read,
                playlist-read-private,
                playlist-modify-private,
                playlist-modify-public,
                user-read-private,
                user-library-modify,
                user-library-read""",
            show_dialog=True,
            open_browser=False,
        )

        return self.auth_manager

    def get_auth_url(self):
        return self.spotipy_auth_manager().get_authorize_url()


class SyncPlaylists:
    def __init__(self, request, playlist_ids, public_playlist):
        self.request = request
        self.playlist_ids = playlist_ids
        self.public_playlist = public_playlist

    def sync_playlists(self):
        sp = spotipy.Spotify(auth_manager=SpotifyAuth(self.request).spotipy_auth_manager())

        spotify_user_id = sp.current_user()["id"]

        all_skipped_songs = {}
        for playlist_id in self.playlist_ids:
            print(playlist_id)
            playlist_to_create = Playlist.objects.filter(
                id=playlist_id
            ).first()
            tracks = Track.objects.filter(
                playlist=playlist_id,
            )

            # Searching Spotify for songs by title and artist
            songs_uris = []
            skipped_songs = []
            for track in tracks:
                search_results = sp.search(
                    q=f"track:{track.track_name}, artist:{track.artist}",
                    type="track",
                )
                try:
                    uri = search_results["tracks"]["items"][0]["uri"]
                    songs_uris.append(uri)
                except IndexError:
                    print(
                        f"{track.track_name} by {track.artist}\
                        doesn't exist in Spotify. Skipped."
                    )
                    skipped_songs.append(f"{track.track_name} by {track.artist}")

            all_skipped_songs[playlist_to_create.playlist_name] = skipped_songs

            # Creating a private playlist
            playlist = sp.user_playlist_create(
                user=spotify_user_id,
                name=playlist_to_create.playlist_name,
                public=self.public_playlist,
            )

            # Adding songs found to the new playlist
            sp.playlist_add_items(
                playlist_id=playlist["id"],
                items=songs_uris,
            )

        return all_skipped_songs
