from django import forms


class YandexAuthForm(forms.Form):
    email = forms.EmailField(
        label="Yandex email",
        max_length=50,
    )
    password = forms.CharField(widget=forms.PasswordInput())
