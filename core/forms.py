import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pulseira, Perfil

# --- FUNÇÃO DE VALIDAÇÃO DE CPF REAL ---
def validar_cpf(value):
    cpf = re.sub(r'\D', '', value) # Remove pontos e traços
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            raise ValidationError('CPF inválido.')

class PulseiraForm(forms.ModelForm):
    class Meta:
        model = Pulseira
        fields = [
            'nome', 'nascimento', 'foto', 'tipo_sanguineo',
            'possui_convenio', 'nome_convenio', 'numero_sus_convenio',
            'condicao_medica', 'alergias', 'medicamentos',
            'instrucoes_abordagem',
            'responsavel_nome', 'responsavel_telefone', 'responsavel_email',
            'aceite_termos'
        ]
        widgets = {
            'nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'condicao_medica': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medicamentos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'instrucoes_abordagem': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class CadastroUsuarioForm(UserCreationForm):
    cpf = forms.CharField(
        label='CPF', 
        max_length=14,
        validators=[validar_cpf],
        widget=forms.TextInput(attrs={'placeholder': '000.000.000-00', 'class': 'form-control'})
    )
    cep = forms.CharField(
        label='CEP',
        max_length=9,
        widget=forms.TextInput(attrs={'placeholder': '00000-000', 'class': 'form-control'})
    )
    logradouro = forms.CharField(
        label='Rua/Avenida',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    numero = forms.CharField(
        label='Número',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº'})
    )
    bairro_cidade = forms.CharField(
        label='Bairro / Cidade',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Definimos os campos que aparecem no formulário
        fields = UserCreationForm.Meta.fields + ('cpf', 'cep', 'logradouro', 'numero', 'bairro_cidade',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Pegamos os dados limpos do formulário
        cpf = self.cleaned_data['cpf']
        cep = self.cleaned_data['cep']
        rua = self.cleaned_data['logradouro']
        num = self.cleaned_data['numero']
        bairro_cidade = self.cleaned_data['bairro_cidade']
        
        # Montamos uma única string de endereço para salvar no campo 'endereco' do seu Model Perfil
        endereco_completo = f"CEP: {cep}, {rua}, {num} - {bairro_cidade}"
        
        # Salva no banco de dados (Modelo Perfil)
        Perfil.objects.update_or_create(
            user=user, 
            defaults={'cpf': cpf, 'endereco': endereco_completo}
        )
        
        return user