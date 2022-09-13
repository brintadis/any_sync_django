from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm
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
