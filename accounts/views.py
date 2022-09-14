from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, SynchronizationForm
from spotify.spotify import SyncPlaylists
from playlist.models import Playlist


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def profile(request, user_id):
    playlists = Playlist.objects.filter(user=user_id).all()

    context = {
        "playlists": playlists,
        "user_id": user_id,
    }

    return render(request, "accounts/profile.html", context=context)


@login_required
def synchronization(request, music_service, user_id):
    playlists = Playlist.objects.filter(user=user_id).all()
    form = SynchronizationForm
    context = {
        "form": form,
        "playlists": playlists,
        "user_id": user_id,
        "music_service": music_service,
    }

    return render(request, "accounts/synchronization.html", context=context)


@login_required
def sync_playlist(request, user_id):
    if request.method == 'POST':
        form = SynchronizationForm(request.POST)
        playlist_ids = form.cleaned_data['playlist']
        print(playlist_ids)
        # music_service = request.POST.get("music_service")
        # public_playlist = request.POST.get("public_playlist") == "True"
        # print(playlist_ids)

        # if music_service == 'Spotify':
        #     print('working with spotify')
        #     sync_to_spotify = SyncPlaylists(request, user_id, playlist_ids, public_playlist)
        #     sync_to_spotify.sync_playlists()
        #     return HttpResponse('working with spotify')
        # elif music_service == 'Yandex Music':
        #     print('working with yandex music')
        #     return HttpResponse('working with yandex music')
    return HttpResponse(playlist_ids)
