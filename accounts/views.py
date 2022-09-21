from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import User
from playlist.models import Playlist

from .forms import CustomUserCreationForm

from ya_music.ya_music import SyncYandexPlaylists, validate_token
from spotify.spotify import SyncSpotifyPlaylists

# from ya_music.tasks import sync_yandex


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
    context = {
        "playlists": playlists,
        "user_id": user_id,
        "music_service": music_service,
    }

    return render(request, "accounts/synchronization.html", context=context)


@login_required
def sync_playlist(request):
    if request.method == 'POST':
        playlist_ids = request.POST.getlist("playlist_id")
        music_service = request.POST.get("music_service")
        public_playlist = request.POST.get("public_playlist") == 'True'
        if music_service == "Spotify":
            sync_playlist = SyncSpotifyPlaylists(
                user_id=request.user.id,
                playlist_ids=playlist_ids,
                public_playlist=public_playlist,
            )

            skipped_songs = sync_playlist.sync_playlists()
            print(skipped_songs)
            # message = "\n\n".join(
            #     f"""Плейлист: {playlist}
            #     Треки:
            #     {", ".join(tracks) if len(tracks) != 1 else "".join(tracks)}"""
            #     for playlist, tracks in skipped_songs.items()
            # )
            # messages.info(request, "Не удалось добавить треки:\n" + message)
            return redirect("profile", user_id=request.user.id)

        elif music_service == "Yandex Music":
            yandex_token = User.objects.filter(id=request.user.id).first().yandex_token
            if validate_token(yandex_token):
                visibility = ['public', 'private'][public_playlist]
                sync_playlist = SyncYandexPlaylists(
                    token=yandex_token,
                    playlist_ids=playlist_ids,
                    visibility=visibility,
                )
                sync_playlist.sync_playlists()
                return redirect("profile", user_id=request.user.id)
            else:
                message = "Пользовательская информация устарела, необходимо повторить авторизацию."
                messages.info(request, )
                return redirect('yandex_auth')
    return HttpResponse("not post")
