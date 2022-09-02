from django.http import HttpResponse
from django.shortcuts import render, redirect


def show_playlist(request, playlist_id):
    return HttpResponse(f"Playlist with id = {playlist_id}")
