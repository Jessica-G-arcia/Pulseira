import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pulseira, Perfil

# --- VALIDAÇÃO DE CPF ---
def validar_cpf(value):
    cpf = re.sub(r'\D', '', value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            raise ValidationError('CPF inválido.')

# --- FORMULÁRIO DA PULSEIRA (O QUE ESTAVA FALTANDO) ---
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

# --- FORMULÁRIO DE CADASTRO DE USUÁRIO ---
class CadastroUsuarioForm(UserCreationForm):
    nome_completo = forms.CharField(label='Nome Completo')
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(label='CPF', max_length=14, validators=[validar_cpf])
    cep = forms.CharField(label='CEP', max_length=9)
    logradouro = forms.CharField(label='Rua/Avenida', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    numero = forms.CharField(label='Número')
    bairro_cidade = forms.CharField(label='Bairro / Cidade', widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nome_completo', 'email', 'cpf', 'cep', 'logradouro', 'numero', 'bairro_cidade')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if Perfil.objects.filter(cpf=cpf).exists():
            raise ValidationError("Este CPF já está cadastrado.")
        return cpf

    def save(self, commit=True):
        user = super().save(commit=False)
        nome_partes = self.cleaned_data['nome_completo'].split(' ', 1)
        user.first_name = nome_partes[0]
        user.last_name = nome_partes[1] if len(nome_partes) > 1 else ""
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            endereco_final = f"CEP: {self.cleaned_data['cep']}, {self.cleaned_data['logradouro']}, {self.cleaned_data['numero']} - {self.cleaned_data['bairro_cidade']}"
            Perfil.objects.update_or_create(
                user=user, 
                defaults={'cpf': self.cleaned_data['cpf'], 'endereco': endereco_final}
            )
        return user