from django.urls import path

from .views import SignUpView, profile, synchronization, sync_playlist

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/<int:user_id>", profile, name="profile"),
    path(
        "synchronization/<int:user_id>/<str:music_service>",
        synchronization,
        name="synchronization"
    ),
    path("sync_playlist", sync_playlist, name="sync_playlist"),
]
