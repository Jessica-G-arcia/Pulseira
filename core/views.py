from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
# Importamos com alias para evitar conflitos com nomes de funções ou variáveis
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.mail import send_mail
from django.conf import settings
from geopy.geocoders import Nominatim
import json

# Imports locais
from .models import Pulseira
from .forms import CadastroUsuarioForm, PulseiraForm

# ========================================================
# ÁREA DE AUTENTICAÇÃO (LOGIN / CADASTRO DE DONO)
# ========================================================

def cadastro_usuario(request):
    """Cria uma conta para o dono das pulseiras (Com CPF e Endereço)"""
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST) 
        if form.is_valid():
            user = form.save()
            # Loga o usuário automaticamente após o cadastro usando o alias
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = CadastroUsuarioForm()
    
    return render(request, 'registration/cadastro_usuario.html', {'form': form})

def fazer_login(request):
    """Exibe a tela de login e processa a autenticação"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# ========================================================
# ÁREA RESTRITA (SOMENTE DONO LOGADO)
# ========================================================

@login_required(login_url='/login/')
def dashboard(request):
    """Painel principal do usuário logado"""
    minhas_pulseiras = Pulseira.objects.filter(usuario=request.user)
    return render(request, 'core/dashboard.html', {'pulseiras': minhas_pulseiras})

@login_required(login_url='/login/')
def criar_pulseira(request):
    """Formulário para adicionar novas pulseiras"""
    if request.method == 'POST':
        form = PulseiraForm(request.POST, request.FILES)
        if form.is_valid():
            nova_pulseira = form.save(commit=False)
            nova_pulseira.usuario = request.user
            nova_pulseira.save()
            return redirect('dashboard')
    else:
        form = PulseiraForm()
    
    return render(request, 'core/cadastro.html', {'form': form})

# ========================================================
# ÁREA PÚBLICA (QR CODE E EMERGÊNCIA)
# ========================================================

def visualizar_pulseira(request, pulseira_id):
    """Página acessada publicamente (ex: via QR Code)"""
    pulseira = get_object_or_404(Pulseira, id=pulseira_id)
    
    if not pulseira.aceite_termos:
       return render(request, 'erro_privacidade.html', status=403)
    
    return render(request, 'core/ver_pulseira.html', {
        'pulseira': pulseira
    })

@csrf_exempt
def api_notificar(request, pulseira_id):
    """Recebe localização GPS e notifica o responsável por e-mail"""
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            lat = dados.get('latitude')
            lon = dados.get('longitude')
            
            pulseira = Pulseira.objects.get(id=pulseira_id)
            if not pulseira.responsavel_email:
                return JsonResponse({'status': 'erro', 'msg': 'Sem email cadastrado'})

            # Geocoding Reverso (GPS -> Endereço)
            endereco = "Endereço aproximado (GPS)"
            try:
                geolocator = Nominatim(user_agent="sistema_sos_v1_jessica")
                local = geolocator.reverse(f"{lat}, {lon}", timeout=5)
                if local:
                    endereco = local.address
            except:
                pass

            # Disparo de E-mail
            assunto = f"🚨 ALERTA SOS: {pulseira.nome} foi encontrado(a)!"
            link_maps = f"https://www.google.com/maps?q={lat},{lon}"
            
            mensagem = f"ALERTA DE EMERGÊNCIA!\n\nA pulseira de {pulseira.nome} foi acionada.\n\n📍 Localização: {endereco}\n🗺️ Google Maps: {link_maps}"
            
            send_mail(
                assunto,
                mensagem,
                settings.EMAIL_HOST_USER,
                [pulseira.responsavel_email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'sucesso'})
        
        except Exception as e:
            return JsonResponse({'status': 'erro', 'msg': str(e)})
            
    return JsonResponse({'status': 'erro', 'msg': 'Método inválido'})