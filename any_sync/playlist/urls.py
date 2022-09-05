from django.urls import path

from .views import add_playlist, show_playlist, delete_playlist, delete_track

urlpatterns = [
    path("<int:playlist_id>/", show_playlist, name="playlist_detail"),
    path(
        "delete-playlist/<int:playlist_id>/<int:user_id>/",
        delete_playlist,
        name="delete_playlist"
    ),
    path(
        "delete-track/<int:track_id>/<int:playlist_id>/",
        delete_track,
        name="delete_track"
    ),
    path("add-playlist/", add_playlist, name="add_playlist")
]
