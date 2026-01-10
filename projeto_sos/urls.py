from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views  # Importa o arquivo views inteiro para evitar erros

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Cadastro (Link que você manda para o cliente)
    path('cadastro/', views.criar_pulseira, name='cadastro_pulseira'),

    # 2. Visualização (Onde o QR Code vai levar)
    # Deixei 'ver/' para o link ficar curto, mas o nome interno é 'visualizar_pulseira'
    path('ver/<uuid:pulseira_id>/', views.visualizar_pulseira, name='visualizar_pulseira'),

    # 3. API do GPS (Botão de Pânico)
    path('api/notificar/<uuid:pulseira_id>/', views.api_notificar, name='api_notificar'),

    # 4. Termos (Só descomente se você tiver criado essa função no views.py)
    # path('termos/', views.pagina_termos, name='termos'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)