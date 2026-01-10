from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # <--- IMPORTANTE: Importar isso
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import Pulseira

# --- PÁGINA PÚBLICA (VISUALIZAR) ---
# Se tiver @login_required aqui em cima, APAGUE. Essa página tem que ser pública!
def visualizar_pulseira(request, pulseira_id):
    pulseira = get_object_or_404(Pulseira, id=pulseira_id)
    return render(request, 'core/visualizar_pulseira.html', {'pulseira': pulseira})

# --- API DE NOTIFICAÇÃO (GPS) ---
@csrf_exempt  # <--- IMPORTANTE: Adicione essa linha em cima da API
def api_notificar(request, pulseira_id):
    if request.method == "POST":
        try:
            pulseira = get_object_or_404(Pulseira, id=pulseira_id)
            dados = json.loads(request.body)
            
            lat = dados.get('latitude')
            lon = dados.get('longitude')
            
            # Monta o link do Google Maps
            link_maps = f"https://www.google.com/maps?q={lat},{lon}"
            
            assunto = f"ALERTA SOS: {pulseira.nome} foi encontrado(a)!"
            mensagem = f"""
            Alerta de Emergência!
            
            A pulseira de {pulseira.nome} foi lida.
            
            Localização aproximada:
            {link_maps}
            
            Entre em contato imediatamente.
            """
            
            # Envia o e-mail (imprime erro no console se falhar, mas não trava o site)
            send_mail(
                assunto,
                mensagem,
                settings.EMAIL_HOST_USER,
                [pulseira.responsavel_email], # Mudei para usar o email do responsável cadastrado
                fail_silently=False,
            )
            
            return JsonResponse({'status': 'sucesso'})
            
        except Exception as e:
            # Isso vai mostrar o erro real no Log de Erro se o email falhar
            print(f"ERRO AO ENVIAR EMAIL: {e}") 
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)

    return JsonResponse({'status': 'erro'}, status=400)