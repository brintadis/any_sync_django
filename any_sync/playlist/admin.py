from django.contrib import admin

from .models import Playlist, Track

admin.site.register(Playlist)
admin.site.register(Track)
