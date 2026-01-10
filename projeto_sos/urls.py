from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import perfil_emergencia, notificar_localizacao, pagina_termos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ver/<uuid:pulseira_id>/', perfil_emergencia, name='perfil'),
    path('api/notificar/<uuid:pulseira_id>/', notificar_localizacao, name='notificar'),
    path('termos/', pagina_termos, name='termos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)