from django.http import HttpResponse


def show_playlist(request, playlist_id):
    return HttpResponse(f"Playlist with id = {playlist_id}")
