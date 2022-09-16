from django.urls import path

from .views import start_spotify_auth, spotify_auth


urlpatterns = [
    path("start-spotify-auth/", start_spotify_auth, name="start_spotify_auth"),
    path("spotify-auth/", spotify_auth, name="spotify_auth")
]
