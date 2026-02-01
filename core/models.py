from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date
from django.utils.safestring import mark_safe

# --- PARTE 1: PULSEIRA E PERFIL (MANTIDA IGUAL) ---

class Pulseira(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # --- DADOS PESSOAIS ---
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='fotos_pulseira', blank=True, null=True)
    nascimento = models.DateField()
    
    TIPOS_SANGUE = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('NA', 'Não sei'),
    ]
    tipo_sanguineo = models.CharField(max_length=3, choices=TIPOS_SANGUE, default='NA', verbose_name="Tipo Sanguíneo")

    # --- PLANO DE SAÚDE / SUS ---
    numero_sus_convenio = models.CharField(max_length=50, blank=True, verbose_name="Número do Cartão SUS")
    OPCOES_SIM_NAO = [('S', 'Sim'), ('N', 'Não')]
    possui_convenio = models.CharField(max_length=1, choices=OPCOES_SIM_NAO, default='N', verbose_name="Possui Convênio Médico?")
    nome_convenio = models.CharField(max_length=100, blank=True, verbose_name="Nome do Convênio", help_text="Digite o nome (e o número da carteirinha, se quiser).")

    # --- SAÚDE ---
    condicao_medica = models.TextField(verbose_name="Condição Médica (Doenças)", blank=True, help_text="Se não houver, deixe em branco.")
    alergias = models.TextField(verbose_name="Alergias", blank=True, help_text="Se não houver, deixe em branco.")
    medicamentos = models.TextField(verbose_name="Medicamentos em Uso", blank=True, help_text="Se não houver, deixe em branco.")

    # --- INSTRUÇÕES ---
    instrucoes_abordagem = models.TextField(blank=True, verbose_name="Como conversar/acalmar?", help_text="Ex: Fale baixo, não toque bruscamente.")
    
    # --- CONTATOS ---
    responsavel_nome = models.CharField(max_length=100, verbose_name="Nome do Responsável")
    responsavel_telefone = models.CharField(max_length=20, verbose_name="Telefone para Contato")
    responsavel_email = models.EmailField(blank=True, null=True, verbose_name="E-mail para Notificação")

    aceite_termos = models.BooleanField(
        default=False,
        verbose_name="Termos de Uso",
        help_text=mark_safe("Ao marcar, você concorda com os <a href='/termos/' target='_blank'>Termos de Uso</a> e autoriza a exibição pública.")
    )

    def save(self, *args, **kwargs):
        if not self.condicao_medica: self.condicao_medica = "Nenhuma"
        if not self.alergias: self.alergias = "Nenhuma"
        if not self.medicamentos: self.medicamentos = "Nenhum"
        super().save(*args, **kwargs)

    def get_condicoes_lista(self):
        return ["Nenhuma"] if not self.condicao_medica or self.condicao_medica == "Nenhuma" else [c.strip() for c in self.condicao_medica.split(',') if c.strip()]

    def get_alergias_lista(self):
        return ["Nenhuma"] if not self.alergias or self.alergias == "Nenhuma" else [a.strip() for a in self.alergias.split(',') if a.strip()]

    def get_medicamentos_lista(self):
        if not self.medicamentos or self.medicamentos == "Nenhum": return []
        texto_limpo = self.medicamentos.replace('\n', ',').replace('\r', '')
        return [m.strip() for m in texto_limpo.split(',') if m.strip()]

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        hoje = date.today()
        return hoje.year - self.nascimento.year - ((hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day))

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    endereco = models.TextField(verbose_name="Endereço Completo")
    creditos_pulseira = models.IntegerField(default=0)

    def __str__(self):
        return f"Perfil de {self.user.username}"


# --- PARTE 2: SISTEMA DE LOJA (CORRIGIDO E ATUALIZADO) ---

class Produto(models.Model):
    TIPO_CHOICES = (
        ('digital', 'Apenas QR Code (Digital)'),
        ('fisico', 'Produto Físico (Adesivo/Resina)'),
    )
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2) # Ex: 39.90
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='fisico')
    imagem_url = models.CharField(max_length=200, blank=True, null=True, help_text="Cole o link de uma imagem ou ícone aqui")

    # --- NOVOS CAMPOS PARA CORREIOS ---
    peso_g = models.IntegerField(default=200, help_text="Peso em gramas (ex: 200)")
    comprimento_cm = models.IntegerField(default=15, help_text="Comprimento em cm (Min 15)")
    largura_cm = models.IntegerField(default=10, help_text="Largura em cm (Min 10)")
    altura_cm = models.IntegerField(default=2, help_text="Altura em cm (Min 2)")

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Pago / Aprovado'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    # ID da transação no Mercado Pago
    id_transacao = models.CharField(max_length=100, blank=True, null=True)

    # --- NOVOS CAMPOS PARA O FRETE ---
    cep_entrega = models.CharField(max_length=9, blank=True, null=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tipo_frete = models.CharField(max_length=50, blank=True) # Ex: SEDEX ou PAC
    prazo_entrega = models.IntegerField(default=0) # Quantos dias chega
    
    # Preço final (Produto + Frete)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} ({self.status})"