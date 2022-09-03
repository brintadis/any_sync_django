"""
Init playlist models
"""
from django.db import models
from django.conf import settings
from django.urls import reverse


class Playlist(models.Model):
    """
    Playlist model
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    playlist_name = models.CharField(null=False, max_length=90, verbose_name="Playlist name")
    owner_name = models.CharField(null=False, max_length=50, verbose_name="Owner name")
    last_update = models.DateTimeField(auto_now_add=True, verbose_name="Last update")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    img_cover_url = models.CharField(
        null=True,
        max_length=255,
        verbose_name="Playlist's cover url"
    )

    class Meta:
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'
        ordering = ['id']

    def __str__(self) -> str:
        """
        Rerp of a Playlist model
        """
        return f"{self.playlist_name} {self.owner_name}"

    def get_absolute_url(self):
        return reverse('playlist', kwargs={'playlist_id': self.pk})

    @property
    def tracks_count(self):
        """
        Playlist's count tracks
        """
        return Track.objects.filter(playlist=self.id).count()


class Track(models.Model):
    """
    Track model
    """
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name="Playlist")
    artist = models.CharField(null=False, max_length=90, verbose_name="Artist")
    track_name = models.CharField(null=False, max_length=255, verbose_name="Track name")
    duration = models.TimeField(null=False, verbose_name="Duration")
    img_cover_url = models.CharField(null=True, max_length=255, verbose_name="Track's cover url")

    class Meta:
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'

    def __str__(self):
        """
        Rerp of a Track model
        """
        return f"{self.track_name} by {self.artist}"
