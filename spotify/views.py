from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .spotify import SpotifyAuth


@login_required
def start_spotify_auth(request):
    auth_url = SpotifyAuth(request).get_auth_url()
    print(auth_url)

    return redirect(auth_url)


@login_required
def spotify_auth(request):
    spotify_auth = SpotifyAuth(request)
    auth_manager = spotify_auth.spotipy_auth_manager()
    auth_manager.get_access_token(request.GET.get("code"))

    return redirect("synchronization", user_id=request.user.id, music_service="Spotify")
