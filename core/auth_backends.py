from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Perfil
import re

class CPFOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        # 1. Tenta buscar pelo E-mail
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        # 2. Tenta buscar pelo CPF (limpo)
        cpf_limpo = re.sub(r'\D', '', username)
        try:
            perfil = Perfil.objects.get(cpf=cpf_limpo)
            user = perfil.user
            if user.check_password(password):
                return user
        except Perfil.DoesNotExist:
            pass

        return None