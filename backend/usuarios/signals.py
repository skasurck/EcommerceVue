from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login


def actualizar_ultimo_acceso(sender, user, request, **kwargs):
    update_last_login(sender, user)


user_logged_in.connect(actualizar_ultimo_acceso)
