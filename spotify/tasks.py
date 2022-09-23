from celery import shared_task

from spotify.spotify import SyncSpotifyPlaylists


@shared_task
def create_playlists_spotify(user_id, playlist_ids, visibility):
    """Creating playlists using spotipy and celery

    Args:
        user_id (`int`): current user id
        playlist_ids (`list`): list of playlist ids to user while creating spotify playlists
        visibility (`Bool`): make a public or a private playlist

    Returns:
        `list`: list of skipped tracks while search using the music service
    """
    sync_playlist = SyncSpotifyPlaylists(
        user_id=user_id,
        playlist_ids=playlist_ids,
        visibility=visibility,
    )

    skipped_songs = sync_playlist.sync_playlists()
    return skipped_songs
