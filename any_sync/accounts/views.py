from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import render

from .forms import CustomUserCreationForm
from playlist.models import Playlist


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def profile(request, user_id):
    playlists = Playlist.objects.filter(user=user_id).all()

    context = {
        "playlists": playlists
    }

    return render(request, "accounts/profile.html", context=context)
