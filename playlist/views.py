from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import SearchPlaylistByUrlForm
from .models import Playlist, Track
from spotify.spotify import ImportSpotifyPlaylistByUrl
from ya_music.ya_music import ImportYandexMusicPlaylistByUrl


@login_required
def import_playlist_by_url(request):
    if request.method == 'POST':
        form = SearchPlaylistByUrlForm(request.POST)
        if form.is_valid():
            playlist_url = form.cleaned_data['playlist_url']
            current_user = request.user

            if 'Spotify' == form.cleaned_data['music_service']:
                try:
                    import_playlist = ImportSpotifyPlaylistByUrl(
                        playlist_url=playlist_url,
                        user=current_user,
                    )
                    import_playlist.get_spotify_playlist_by_url()
                    messages.info(request, "Плейлист успешно добавлен")
                    return redirect('profile', user_id=current_user.id)
                except Exception:
                    messages.error(request, 'Несуществующий плейлист в Spotify')
                    return redirect('import_playlist_by_url')
            elif 'Yandex Music' == form.cleaned_data['music_service']:
                try:
                    import_playlist = ImportYandexMusicPlaylistByUrl(
                        playlist_url=playlist_url,
                        user=current_user,
                    )
                    import_playlist.get_yandex_playlist_by_url()
                    messages.info(request, "Плейлист успешно добавлен")
                    return redirect('profile', user_id=current_user.id)
                except Exception:
                    messages.error(request, 'Несуществующий плейлист в Yandex Music')
                    return redirect('import_playlist_by_url')

            return redirect('home')
    else:
        form = SearchPlaylistByUrlForm()

    return render(request, 'playlist/search_playlist_by_url.html', {'form': form})


@login_required
def show_playlist(request, playlist_id):
    current_playlist = Playlist.objects.filter(id=playlist_id).first()
    tracks = Track.objects.filter(playlist=playlist_id).all()

    context = {
        'current_playlist': current_playlist,
        'tracks': tracks,
    }

    return render(request, 'playlist/playlist_detail.html', context=context)


@login_required
def delete_playlist(request, playlist_id, user_id):
    """Delete a playlist from the DB.

    Args:
        playlist_id (`int`): Playlist's id to update
        user_id (`int`): current user id.
    """
    Playlist.objects.filter(id=playlist_id).delete()

    return redirect('profile', user_id=user_id)


@login_required
def delete_track(request, track_id, playlist_id):
    """Delete track and update Playlist last update time.

    Args:
        track_id (`int`): Track's id to delete
        playlist_id (`int`): Playlist's id to update
    """
    Track.objects.filter(id=track_id).delete()
    playlist_to_update = Playlist.objects.filter(id=playlist_id).first()
    playlist_to_update.last_update = datetime.now()
    playlist_to_update.save()

    return redirect('playlist_detail', playlist_id=playlist_id)
