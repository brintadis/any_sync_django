from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import SearchPlaylistByUrlForm
from .models import Playlist, Track
from spotify.spotify import ImportSpotifyPlaylistByUrl
from ya_music.ya_music import ImportYandexMusicPlaylistByUrl


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
                    return redirect('profile', user_id=current_user.id)
                except Exception:
                    messages.error(request, 'Несуществующий плейлист в Yandex Music')
                    return redirect('import_playlist_by_url')

            return redirect('home')
    else:
        form = SearchPlaylistByUrlForm()

    return render(request, 'playlist/search_playlist_by_url.html', {'form': form})


def show_playlist(request, playlist_id):
    current_playlist = Playlist.objects.filter(id=playlist_id).first()
    tracks = Track.objects.filter(playlist=playlist_id).all()

    context = {
        'current_playlist': current_playlist,
        'tracks': tracks,
    }

    return render(request, 'playlist/playlist_detail.html', context=context)


def delete_playlist(request, playlist_id, user_id):
    Playlist.objects.filter(id=playlist_id).delete()

    return redirect('profile', user_id=user_id)


def delete_track(request, track_id, playlist_id):
    Track.objects.filter(id=track_id).delete()

    return redirect('playlist_detail', playlist_id=playlist_id)
