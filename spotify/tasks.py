from celery import shared_task

from spotify.spotify import SyncSpotifyPlaylists


@shared_task
def create_playlists_spotify(user_id, playlist_ids, visibility):
    sync_playlist = SyncSpotifyPlaylists(
        user_id=user_id,
        playlist_ids=playlist_ids,
        visibility=visibility,
    )

    skipped_songs = sync_playlist.sync_playlists()
    return skipped_songs
