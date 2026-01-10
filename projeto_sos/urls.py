from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core import views  # Importa o arquivo views inteiro para evitar erros

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ÁREA DO DONO ---
    path('', views.dashboard, name='home'), # Raiz vai pro dashboard (se logado)
    path('cadastro-conta/', views.cadastro_usuario, name='cadastro_usuario'),
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('painel/', views.dashboard, name='dashboard'),
    
    path('adicionar-pulseira/', views.criar_pulseira, name='criar_pulseira'),

    # --- ÁREA PÚBLICA (QR CODE) - ISSO MANTÉM SEU TESTE FUNCIONANDO ---
    path('ver/<uuid:pulseira_id>/', views.ver_pulseira, name='ver_pulseira'),
    path('api/notificar/<uuid:pulseira_id>/', views.api_notificar, name='api_notificar'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)