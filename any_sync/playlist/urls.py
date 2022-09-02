from django.urls import path, re_path

from .views import *

urlpatterns = [
    path("<int:playlist_id>/", show_playlist, name="playlist")
]