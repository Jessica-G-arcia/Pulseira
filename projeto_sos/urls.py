from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ÁREA DO DONO ---
    path('', views.dashboard, name='home'), 
    path('cadastro-conta/', views.cadastro_usuario, name='cadastro_usuario'),
    
    # CORREÇÃO 1: Apontar para 'views.fazer_login' em vez de 'views.login'
    path('login/', views.fazer_login, name='login'),

    # Rotas de Esqueci a Senha
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetSentView.as_view(template_name="registration/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    
    # Logout (O Django já fornece a view pronta, mas precisamos garantir o redirect)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('painel/', views.dashboard, name='dashboard'),
    path('adicionar-pulseira/', views.criar_pulseira, name='criar_pulseira'),

    # --- ÁREA PÚBLICA (QR CODE) ---
    # CORREÇÃO 2: Apontar para 'views.visualizar_pulseira'
    # CORREÇÃO 3: O 'name' deve ser igual ao usado no HTML ({% url 'visualizar_pulseira' ... %})
    path('ver/<uuid:pulseira_id>/', views.visualizar_pulseira, name='visualizar_pulseira'),
    
    path('api/notificar/<uuid:pulseira_id>/', views.api_notificar, name='api_notificar'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)