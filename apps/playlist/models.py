from django.db import models

from apps.accounts.models import User


class Playlist(models.Models):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_name = models.CharField(null=False)
    owner_name = models.CharField(null=False)
    last_update = models.DateTimeField(null=False)
    description = models.TextField(null=True)
    img_cover_url = models.CharField(null=True)

    def __str__(self) -> str:
        return f"{self.playlist_name} {self.owner_name}"

    def tracks_count(self):
        return Track.objects.filter(playlist=self.playlist).count
    


class Track(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    artist = models.CharField(null=False)
    track_name = models.CharField(null=False)
    duration = models.TimeField(null=False)
    img_cover_url = models.CharField(null=True)

    def __str__(self):
        return f"{self.track_name} by {self.artist}"
