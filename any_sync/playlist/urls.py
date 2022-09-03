from django.urls import path

from .views import show_playlist

urlpatterns = [
    path("<int:playlist_id>/", show_playlist, name="playlist"),
]
