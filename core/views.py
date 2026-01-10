from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from geopy.geocoders import Nominatim
import json

# Imports locais
from .models import Pulseira
from .forms import PulseiraForm, CadastroUsuarioForm

# ========================================================
# ÁREA DE AUTENTICAÇÃO (LOGIN / CADASTRO DE DONO)
# ========================================================

def cadastro_usuario(request):
    """Cria uma conta para o dono das pulseiras (AGORA COM CPF)"""
    if request.method == 'POST':
        # Usa o nosso form personalizado
        form = CadastroUsuarioForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CadastroUsuarioForm()
    
    return render(request, 'registration/cadastro_usuario.html', {'form': form})

def fazer_login(request):
    """Tela de Login"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# ========================================================
# ÁREA RESTRITA (SOMENTE DONO LOGADO)
# ========================================================

@login_required(login_url='/login/')
def dashboard(request):
    """Painel principal: Mostra as pulseiras do usuário"""
    # Filtra: Traz apenas as pulseiras onde usuario = usuario_logado
    minhas_pulseiras = Pulseira.objects.filter(usuario=request.user)
    return render(request, 'core/dashboard.html', {'pulseiras': minhas_pulseiras})

@login_required(login_url='/login/')
def criar_pulseira(request):
    """Adiciona uma nova pulseira vinculada à conta"""
    if request.method == 'POST':
        form = PulseiraForm(request.POST, request.FILES)
        if form.is_valid():
            # Cria o objeto na memória, mas não salva no banco ainda
            nova_pulseira = form.save(commit=False)
            # Vincula ao usuário logado
            nova_pulseira.usuario = request.user
            # Agora salva de verdade
            nova_pulseira.save()
            
            # Redireciona para o painel
            return redirect('dashboard')
    else:
        form = PulseiraForm()
    
    return render(request, 'core/cadastro.html', {'form': form})

# ========================================================
# ÁREA PÚBLICA (QR CODE / RESGATE / EMERGÊNCIA)
# ========================================================

def visualizar_pulseira(request, pulseira_id):
    """
    Página Pública: Acessada via QR Code.
    NÃO pede login, pois quem achou a pessoa precisa ver os dados rápido.
    """
    pulseira = get_object_or_404(Pulseira, id=pulseira_id)
    
    # Verifica termos de uso (se o campo existir e for obrigatório)
    if not pulseira.aceite_termos:
       return render(request, 'erro_privacidade.html', status=403)
    
    return render(request, 'core/visualizar_pulseira.html', {
        'pulseira': pulseira
    })

@csrf_exempt
def api_notificar(request, pulseira_id):
    """
    API Invisível: Recebe o GPS do botão de pânico e envia e-mail.
    """
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            lat = dados.get('latitude')
            lon = dados.get('longitude')
            
            pulseira = Pulseira.objects.get(id=pulseira_id)
            
            if not pulseira.responsavel_email:
                return JsonResponse({'status': 'erro', 'msg': 'Sem email cadastrado'})

            # Tenta converter coordenadas em endereço (Geocoding Reverso)
            endereco = "Endereço aproximado (GPS)"
            try:
                geolocator = Nominatim(user_agent="sistema_sos_v1_jessica")
                local = geolocator.reverse(f"{lat}, {lon}", timeout=5)
                if local:
                    endereco = local.address
            except:
                endereco = "Endereço não identificado (Erro de conexão)"

            # Prepara o E-mail
            assunto = f"ALERTA SOS: {pulseira.nome} foi encontrado(a)!"
            link_maps = f"http://maps.google.com/?q={lat},{lon}"
            
            mensagem = f"""
            🚨 ALERTA DE EMERGÊNCIA!
            
            A pulseira de {pulseira.nome} acabou de ser escaneada/acionada.
            
            📍 Localização Aproximada (Endereço):
            {endereco}
            
            🗺️ Abrir no Google Maps:
            {link_maps}
            
            Entre em contato imediatamente pelo telefone disponível no perfil.
            """
            
            send_mail(
                assunto,
                mensagem,
                settings.EMAIL_HOST_USER, # Remetente (seu Gmail)
                [pulseira.responsavel_email], # Destinatário (Família)
                fail_silently=False,
            )

            return JsonResponse({'status': 'sucesso'})
        
        except Exception as e:
            print(f"ERRO AO ENVIAR EMAIL: {e}")
            return JsonResponse({'status': 'erro', 'msg': str(e)})
            
    return JsonResponse({'status': 'erro', 'msg': 'Método inválido'})