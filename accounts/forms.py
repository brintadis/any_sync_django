from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("username", "email")


class SynchronizationForm(forms.Form):
    choices = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )
    public_playlist = forms.RadioSelect(
        choices=(
            (True, "Да"),
            (False, "Нет"),
        ),
    ),
    music_service = forms.RadioSelect()
