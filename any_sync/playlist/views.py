from django.shortcuts import render, redirect

from .forms import SearchPlaylistByUrlForm
from .models import Playlist, Track


def add_playlist(request):
    if request.method == 'POST':
        form = SearchPlaylistByUrlForm(request.POST)
        print(form.is_valid)
        if form.is_valid():
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
