from django.db import models
import uuid
from datetime import date
from django.utils.safestring import mark_safe

class Pulseira(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
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
    
    numero_sus_convenio = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Número do Cartão SUS"
    )

    OPCOES_SIM_NAO = [('S', 'Sim'), ('N', 'Não')]
    
    possui_convenio = models.CharField(
        max_length=1,
        choices=OPCOES_SIM_NAO,
        default='N',
        verbose_name="Possui Convênio Médico?"
    )

    nome_convenio = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nome do Convênio",
        help_text="Digite o nome (e o número da carteirinha, se quiser). Ex: Unimed - 123456"
    )

    # --- SAÚDE ---
    condicao_medica = models.TextField(
        verbose_name="Condição Médica (Doenças)", 
        blank=True, 
        help_text="Se não houver, deixe em branco. Separe por vírgula (ex: Diabetes, Hipertensão)."
    )

    # Alergias
    alergias = models.TextField(
        verbose_name="Alergias", 
        blank=True, 
        help_text="Se não houver, deixe em branco. Separe por vírgula (ex: Penicilina, Amendoim)."
    )
    
    # Medicamentos
    medicamentos = models.TextField(
        verbose_name="Medicamentos em Uso", 
        blank=True,
        help_text="Separe os remédios por vírgula ou uma linha abaixo da outra."
    )

    # --- INSTRUÇÕES ---
    instrucoes_abordagem = models.TextField(
        blank=True, 
        verbose_name="Como conversar/acalmar?", 
        help_text="Ex: Fale baixo, não toque bruscamente, ofereça água."
    )
    
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
        """
        Verifica campos vazios antes de salvar e preenche com padrão.
        """
        # Condições Médicas
        if not self.condicao_medica:
            self.condicao_medica = "Nenhuma"
            
        # Alergias
        if not self.alergias:
            self.alergias = "Nenhuma"
            
        # Medicamentos
        if not self.medicamentos:
            self.medicamentos = "Nenhum"
        
        super().save(*args, **kwargs)

    # --- MÉTODOS AUXILIARES PARA O TEMPLATE ---

    def get_condicoes_lista(self):
        if not self.condicao_medica or self.condicao_medica == "Nenhuma":
            return ["Nenhuma"]
        return [c.strip() for c in self.condicao_medica.split(',') if c.strip()]

    def get_alergias_lista(self):
        if not self.alergias or self.alergias == "Nenhuma":
            return ["Nenhuma"]
        return [a.strip() for a in self.alergias.split(',') if a.strip()]

    def get_medicamentos_lista(self):
        if not self.medicamentos or self.medicamentos == "Nenhum":
            return [] # Retorna vazio para o template controlar a mensagem "Nenhum cadastrado"
        
        # Substitui quebras de linha por vírgula para tratar tudo igual
        texto_limpo = self.medicamentos.replace('\n', ',').replace('\r', '')
        
        return [m.strip() for m in texto_limpo.split(',') if m.strip()]

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        hoje = date.today()
        return hoje.year - self.nascimento.year - ((hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day))