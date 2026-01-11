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
    path('login/', views.fazer_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('meu-perfil/', views.editar_perfil, name='editar_perfil'),
    path('painel/', views.dashboard, name='dashboard'),
    path('adicionar-pulseira/', views.criar_pulseira, name='criar_pulseira'),
    path('editar-pulseira/<uuid:pulseira_id>/', views.editar_pulseira, name='editar_pulseira'),
    path('excluir-pulseira/<uuid:pulseira_id>/', views.excluir_pulseira, name='excluir_pulseira'),
    path('termos/', views.termos_uso, name='termos_uso'),
    path('robots.txt', views.robots_txt),

    # --- FLUXO DE ESQUECI A SENHA (CORRIGIDO) ---
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), 
         name="reset_password"),
    
    # CORREÇÃO AQUI: Mudado de PasswordResetSentView para PasswordResetDoneView
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"), 
         name="password_reset_done"),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), 
         name="password_reset_confirm"),
    
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), 
         name="password_reset_complete"),

    # --- ÁREA PÚBLICA ---
    path('ver/<uuid:pulseira_id>/', views.visualizar_pulseira, name='visualizar_pulseira'),
    path('api/notificar/<uuid:pulseira_id>/', views.api_notificar, name='api_notificar'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)