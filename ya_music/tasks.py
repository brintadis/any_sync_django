from celery import shared_task

from .ya_music import SyncYandexPlaylists


@shared_task
def create_playlists_yandex(token, playlist_ids, visibility):
    sync_playlist = SyncYandexPlaylists(
        token=token,
        playlist_ids=playlist_ids,
        visibility=visibility,
    )
    sync_playlist.sync_playlists()
