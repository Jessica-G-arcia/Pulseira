from django.contrib import admin
from .models import Pulseira, Perfil

@admin.register(Pulseira)
class PulseiraAdmin(admin.ModelAdmin):
    # Colunas que aparecem na lista de pulseiras
    list_display = ('nome', 'idade_visual', 'tipo_sanguineo', 'responsavel_telefone')
    search_fields = ('nome', 'responsavel_nome')
    
    # Organização visual do formulário (Grupos)
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'nascimento', 'foto', 'tipo_sanguineo', 'aceite_termos')
        }),
        ('Convênio e SUS', {
            'fields': ('possui_convenio', 'nome_convenio', 'numero_sus_convenio'),
            'description': 'Selecione SIM no convênio para digitar o nome.'
        }),
        ('Saúde', {
            'fields': ('condicao_medica', 'alergias', 'medicamentos'),
            'classes': ('collapse',), # Deixa essa parte "encolhida" para não poluir, clique para abrir
        }),
        ('Instruções', {
            'fields': ('instrucoes_abordagem',)
        }),
        ('Contato de Emergência', {
            'fields': ('responsavel_nome', 'responsavel_telefone', 'responsavel_email')
        }),
    )

    # Função auxiliar para mostrar idade na lista
    def idade_visual(self, obj):
        return f"{obj.idade} anos"
    idade_visual.short_description = "Idade"

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'endereco')
    search_fields = ('user__username', 'cpf')