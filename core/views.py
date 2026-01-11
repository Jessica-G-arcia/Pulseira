from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.http import HttpResponse
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
from .forms import CadastroUsuarioForm, PulseiraForm, EditarUsuarioForm

# ========================================================
# 1. ÁREA DE AUTENTICAÇÃO (LOGIN / CADASTRO / LOGOUT)
# ========================================================

def cadastro_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST) 
        if form.is_valid():
            user = form.save()
            
            # --- O PULO DO GATO ---
            # Dizemos: "Esse usuário é válido no banco de dados padrão"
            # Isso permite que ele entre direto sem digitar a senha de novo
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            # ----------------------
            
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = CadastroUsuarioForm()
    
    return render(request, 'registration/cadastro_usuario.html', {'form': form})
    
    return render(request, 'registration/cadastro_usuario.html', {'form': form})

def fazer_login(request):
    """Faz o login aplicando o CSS correto nos campos"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
        # Se cair aqui, é porque o formulário tem erros
    else:
        form = AuthenticationForm()

    # Configura placeholders e CSS para o template (mesmo em caso de erro)
    form.fields['username'].widget.attrs.update({
        'class': 'form-control', 
        'placeholder': 'Digite o seu CPF ou e-mail'
    })
    form.fields['password'].widget.attrs.update({
        'class': 'form-control', 
        'placeholder': 'Digite a sua senha'
    })
        
    return render(request, 'registration/login.html', {'form': form})

# ========================================================
# 2. ÁREA RESTRITA (GERENCIAMENTO DE PULSEIRAS)
# ========================================================
@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EditarUsuarioForm(instance=request.user)
        
    return render(request, 'core/editar_perfil.html', {'form': form})

@login_required(login_url='/login/')
def dashboard(request):
    """Painel principal: Lista as pulseiras do usuário logado"""
    # Filtra apenas as pulseiras criadas por este usuário
    minhas_pulseiras = Pulseira.objects.filter(usuario=request.user)
    return render(request, 'core/dashboard.html', {'pulseiras': minhas_pulseiras})

@login_required(login_url='/login/')
def criar_pulseira(request):
    """Formulário para adicionar novas pulseiras"""
    if request.method == 'POST':
        form = PulseiraForm(request.POST, request.FILES)
        if form.is_valid():
            nova_pulseira = form.save(commit=False)
            nova_pulseira.usuario = request.user # Vincula ao dono logado
            nova_pulseira.save()
            return redirect('dashboard')
    else:
        form = PulseiraForm()
    
    return render(request, 'core/cadastro.html', {'form': form})

@login_required(login_url='/login/')
def editar_pulseira(request, pulseira_id):
    """Edita os dados de uma pulseira existente"""
    # get_object_or_404 com usuario=request.user garante que ninguém edite a pulseira de outro
    pulseira = get_object_or_404(Pulseira, id=pulseira_id, usuario=request.user)

    if request.method == 'POST':
        # instance=pulseira diz ao formulário para atualizar este item, não criar um novo
        form = PulseiraForm(request.POST, request.FILES, instance=pulseira)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # Preenche o formulário com os dados atuais do banco
        form = PulseiraForm(instance=pulseira)

    return render(request, 'core/editar_pulseira.html', {'form': form, 'pulseira': pulseira})

@login_required(login_url='/login/')
def excluir_pulseira(request, pulseira_id):
    """Exclui uma pulseira (opcional, requer url configurada)"""
    pulseira = get_object_or_404(Pulseira, id=pulseira_id, usuario=request.user)
    if request.method == 'POST':
        pulseira.delete()
        return redirect('dashboard')
    # Se tentar acessar via GET, mandamos de volta para o dashboard por segurança
    return redirect('dashboard')

# ========================================================
# 3. ÁREA PÚBLICA (QR CODE E EMERGÊNCIA)
# ========================================================

def visualizar_pulseira(request, pulseira_id):
    """Página pública acessada via QR Code"""
    pulseira = get_object_or_404(Pulseira, id=pulseira_id)
    
    # Verifica se o usuário aceitou os termos de privacidade
    if not pulseira.aceite_termos:
       return render(request, 'erro_privacidade.html', status=403)
    
    return render(request, 'core/ver_pulseira.html', {
        'pulseira': pulseira
    })

@csrf_exempt
def api_notificar(request, pulseira_id):
    """API: Recebe GPS e envia e-mail de alerta"""
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            lat = dados.get('latitude')
            lon = dados.get('longitude')
            
            pulseira = Pulseira.objects.get(id=pulseira_id)
            if not pulseira.responsavel_email:
                return JsonResponse({'status': 'erro', 'msg': 'Sem email cadastrado'})

            # Tenta converter GPS em Endereço (Rua, Bairro...)
            endereco = "Endereço aproximado (GPS)"
            try:
                geolocator = Nominatim(user_agent="sistema_sos_v1_jessica")
                local = geolocator.reverse(f"{lat}, {lon}", timeout=5)
                if local:
                    endereco = local.address
            except:
                pass # Se falhar, manda só o link do mapa

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

def termos_uso(request):
    """Exibe a página de termos de uso"""
    return render(request, 'core/termos.html')

def robots_txt(request):
    """Diz aos robôs de busca para não indexarem nada do site"""
    linhas = [
        "User-agent: *",  # Para todos os robôs (Google, Bing, Yahoo...)
        "Disallow: /",    # Bloqueie TUDO a partir da raiz
    ]
    return HttpResponse("\n".join(linhas), content_type="text/plain")