from celery import shared_task

from .ya_music import SyncYandexPlaylists


@shared_task
def create_playlists_yandex(token, playlist_ids, visibility):
    """Create yandex music playlist using Celery

    Args:
        token (`str`): yandex api token
        playlist_ids (`list`): DB playlist ids
        visibility (`str`): make a playlist public or private
    """
    sync_playlist = SyncYandexPlaylists(
        token=token,
        playlist_ids=playlist_ids,
        visibility=visibility,
    )
    sync_playlist.sync_playlists()
