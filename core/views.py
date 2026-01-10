from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from geopy.geocoders import Nominatim
from django.conf import settings
import json
from .models import Pulseira
from .forms import PulseiraForm

# 1. Exibe o Perfil (Lê o QR Code)
def perfil_emergencia(request, pulseira_id):
    pulseira = get_object_or_404(Pulseira, id=pulseira_id)
    
    # Verifica se aceitou os termos
    if not pulseira.aceite_termos:
        return render(request, 'erro_privacidade.html', status=403)
    
    # Prepara a lista de remédios
    lista_remedios = pulseira.medicamentos.split('\n')
    
    return render(request, 'perfil.html', {
        'pulseira': pulseira,
        'lista_remedios': lista_remedios
    })

# 2. Recebe a localização e envia email
@csrf_exempt
def notificar_localizacao(request, pulseira_id):
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
            assunto = f"ALERTA: Pulseira de {pulseira.nome} lida!"
            mensagem = f"""
            Atenção! A pulseira foi escaneada.
            
            Local aproximado: {endereco}
            
            Ver no Mapa: http://maps.google.com/?q={lat},{lon}
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
            return JsonResponse({'status': 'erro', 'msg': str(e)})
            
    return JsonResponse({'status': 'erro', 'msg': 'Método inválido'})

# 3. Página de Termos
def pagina_termos(request):
    return render(request, 'termos.html')

# 4. Criação de nova Pulseira Perfil Público
def criar_pulseira(request):
    if request.method == 'POST':
        form = PulseiraForm(request.POST, request.FILES)
        if form.is_valid():
            nova_pulseira = form.save()
            # Redireciona para a página da pulseira criada para ele ver como ficou
            return redirect('visualizar_pulseira', pulseira_id=nova_pulseira.id)
    else:
        form = PulseiraForm()
    
    return render(request, 'core/cadastro.html', {'form': form})
