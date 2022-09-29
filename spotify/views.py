from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .spotify import SpotifyAuth


@login_required
def start_spotify_auth(request):
    """Requesting spotify auth url then redirect.
    """
    auth_url = SpotifyAuth(request).get_auth_url()
    print(auth_url)

    return redirect(auth_url)


@login_required
def spotify_auth(request):
    """Get auth token after auth.
    """
    spotify_auth = SpotifyAuth(request.user.id)
    code = request.GET.get('code')
    auth_manager = spotify_auth.spotipy_auth_manager()
    auth_manager.get_access_token(code, as_dict=True)
    # print(token)

    return redirect("synchronization", user_id=request.user.id, music_service="Spotify")
