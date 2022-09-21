from django.urls import path

from .views import yandex_auth, user_has_token


urlpatterns = [
    path("yadnex-auth/", yandex_auth, name="yandex_auth"),
    path("user-has-token", user_has_token, name="user_has_token")
]
