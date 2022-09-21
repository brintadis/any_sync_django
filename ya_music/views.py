from django.shortcuts import render, redirect
from django.contrib import messages


from .forms import YandexAuthForm
from .ya_music import YandexAuth
from accounts.models import User


def user_has_token(request):
    user_to_check = User.objects.filter(id=request.user.id).first()
    if user_to_check.yandex_token:
        return redirect(
                "synchronization",
                user_id=request.user.id,
                music_service="Yandex Music"
            )
    else:
        return redirect('yandex_auth')


def yandex_auth(request):
    if request.method == 'POST':
        form = YandexAuthForm(request.POST)
        message = "Неправильное имя пользователя или пароль"
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            token, message = YandexAuth(email, password).yandex_auth()
            if token:
                messages.info(request, message)
                # Adding yandex token into the current user model
                user_to_update = User.objects.filter(id=request.user.id).first()
                user_to_update.yandex_token = token
                user_to_update.save()
                return redirect(
                    "synchronization",
                    user_id=request.user.id,
                    music_service="Yandex Music"
                )
        messages.error(request, message)

    else:
        form = YandexAuthForm()

    return render(request, 'yandex/yandex_auth.html', {'form': form})
