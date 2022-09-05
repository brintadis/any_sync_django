from django import forms


MUSIC_SERVICE_CHOICES = (
    ("Spotify", "Spotify"),
    ("Yandex Music", "Yandex Music"),
)


class SearchPlaylistByUrlForm(forms.Form):
    playlist_url = forms.URLField(label="Playlist's URL", max_length=180)
    music_service = forms.ChoiceField(label="Music service", choices=MUSIC_SERVICE_CHOICES)
