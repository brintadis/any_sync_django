from django.shortcuts import render, redirect

from .models import Playlist, Track


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
