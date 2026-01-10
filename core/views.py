from django.shortcuts import render, get_object_or_404, redirect # <--- Faltava o redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from geopy.geocoders import Nominatim
from django.conf import settings
import json
from .models import Pulseira
from .forms import PulseiraForm

# 1. Exibe o Perfil (Nome alinhado com urls.py)
def visualizar_pulseira(request, pulseira_id):
    pulseira = get_object_or_404(Pulseira, id=pulseira_id)
    
    # Se você ainda não rodou a migration do aceite_termos, comente as 3 linhas abaixo
    if not pulseira.aceite_termos:
       return render(request, 'erro_privacidade.html', status=403)
    
    # O template 'core/visualizar_pulseira.html' já pega os remédios direto do model,
    # não precisa passar lista_remedios aqui.
    
    return render(request, 'core/visualizar_pulseira.html', {
        'pulseira': pulseira
    })

# 2. Recebe a localização e envia email (Nome alinhado com urls.py)
@csrf_exempt
def api_notificar(request, pulseira_id):
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            lat = dados.get('latitude')
            lon = dados.get('longitude')
            
            pulseira = Pulseira.objects.get(id=pulseira_id)
            
            if not pulseira.responsavel_email:
                return JsonResponse({'status': 'erro', 'msg': 'Sem email cadastrado'})

            # Converte GPS em Endereço
            geolocator = Nominatim(user_agent="sistema_sos_v1")
            try:
                local = geolocator.reverse(f"{lat}, {lon}")
                endereco = local.address if local else "Endereço não identificado"
            except:
                endereco = "Erro ao buscar endereço exato"

            # Envia Email
            assunto = f"ALERTA SOS: {pulseira.nome} foi encontrado(a)!"
            
            # Link padrão do Google Maps que funciona em Android e iPhone
            link_maps = f"https://www.google.com/maps?q={lat},{lon}"
            
            mensagem = f"""
            ALERTA DE EMERGÊNCIA!
            
            A pulseira de {pulseira.nome} acabou de ser lida.
            
            📍 Local Aproximado:
            {endereco}
            
            🗺️ Ver no Mapa:
            {link_maps}
            """
            
            send_mail(
                assunto,
                mensagem,
                settings.EMAIL_HOST_USER,
                [pulseira.responsavel_email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'sucesso'})
        
        except Exception as e:
            print(f"ERRO EMAIL: {e}") # Ajuda a ver no log
            return JsonResponse({'status': 'erro', 'msg': str(e)})
            
    return JsonResponse({'status': 'erro', 'msg': 'Método inválido'})

# 3. Criação de nova Pulseira (Cadastro Público)
def criar_pulseira(request):
    if request.method == 'POST':
        form = PulseiraForm(request.POST, request.FILES)
        if form.is_valid():
            nova_pulseira = form.save()
            # Redireciona para a visualização correta
            return redirect('visualizar_pulseira', pulseira_id=nova_pulseira.id)
    else:
        form = PulseiraForm()
    
    return render(request, 'core/cadastro.html', {'form': form})

# 4. Termos (Opcional, se tiver o template)
def pagina_termos(request):
    return render(request, 'termos.html')