from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Pulseira, Perfil, Produto, Pedido

# ==================================================
# 1. VISUALIZAÇÃO DENTRO DO USUÁRIO (INLINES)
# ==================================================

class PulseiraInline(admin.TabularInline):
    """Mostra uma lista compacta das pulseiras dentro da tela do Usuário"""
    model = Pulseira
    extra = 0 # Não mostra linhas vazias extras
    fields = ('nome', 'nascimento', 'responsavel_telefone', 'foto')
    readonly_fields = ('nome', 'nascimento', 'responsavel_telefone', 'foto')
    show_change_link = True # Cria um botão para ir editar a pulseira completa
    can_delete = False

class PerfilInline(admin.StackedInline):
    """Mostra o CPF e Endereço dentro da tela do Usuário"""
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Dados Complementares (CPF/Endereço)'
    fields = ('cpf', 'endereco', 'creditos_pulseira')

# ==================================================
# 2. ATUALIZAÇÃO DO ADMIN DE USUÁRIO
# ==================================================

class UserAdmin(BaseUserAdmin):
    # Adiciona os blocos (Pulseiras e Perfil) dentro da edição do usuário
    inlines = (PerfilInline, PulseiraInline)
    
    # Adiciona a coluna CPF na lista de usuários
    list_display = ('username', 'first_name', 'email', 'get_cpf', 'is_staff')
    
    def get_cpf(self, instance):
        if hasattr(instance, 'perfil'):
            return instance.perfil.cpf
        return '-'
    get_cpf.short_description = 'CPF'

# ==================================================
# 3. ADMIN DE PULSEIRA (SEU CÓDIGO MELHORADO)
# ==================================================

@admin.register(Pulseira)
class PulseiraAdmin(admin.ModelAdmin):
    # Adicionei 'get_dono' na lista
    list_display = ('nome', 'get_dono', 'idade_visual', 'tipo_sanguineo', 'responsavel_telefone')
    
    # Filtros novos: Por Usuário e Tipo Sanguíneo
    list_filter = ('usuario', 'tipo_sanguineo')
    
    # Busca expandida: Procura por nome da pulseira E nome do dono
    search_fields = ('nome', 'responsavel_nome', 'usuario__first_name', 'usuario__username')
    
    # Mantive seus Fieldsets, mas adicionei o campo 'usuario' no primeiro grupo
    fieldsets = (
        ('Identificação', {
            'fields': ('usuario', 'nome', 'nascimento', 'foto', 'tipo_sanguineo', 'aceite_termos')
        }),
        ('Convênio e SUS', {
            'fields': ('possui_convenio', 'nome_convenio', 'numero_sus_convenio'),
            'description': 'Selecione SIM no convênio para digitar o nome.'
        }),
        ('Saúde', {
            'fields': ('condicao_medica', 'alergias', 'medicamentos'),
            'classes': ('collapse',), 
        }),
        ('Instruções', {
            'fields': ('instrucoes_abordagem',)
        }),
        ('Contato de Emergência', {
            'fields': ('responsavel_nome', 'responsavel_telefone', 'responsavel_email')
        }),
    )

    # Função para mostrar idade
    def idade_visual(self, obj):
        return f"{obj.idade} anos"
    idade_visual.short_description = "Idade"

    # Função para mostrar o Dono (Nome ou Username)
    def get_dono(self, obj):
        if obj.usuario:
            return f"{obj.usuario.first_name} {obj.usuario.last_name}" or obj.usuario.username
        return "Sem dono"
    get_dono.short_description = "Dono da Conta"
    get_dono.admin_order_field = 'usuario'

# ==================================================
# 4. REGISTRO FINAL
# ==================================================

# Remove o admin padrão de usuários e coloca o nosso novo
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# O Perfil já aparece dentro do User, mas se quiser ele solto também:
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'endereco')
    search_fields = ('user__username', 'cpf')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'preco')
    search_fields = ('nome',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'produto', 'data_pedido', 'status')
    list_filter = ('status', 'data_pedido')
    search_fields = ('usuario__username', 'usuario__email')
    readonly_fields = ('data_pedido',)