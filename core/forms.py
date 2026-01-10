from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pulseira, Perfil

class PulseiraForm(forms.ModelModelForm):
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
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bairro_cidade = forms.CharField(
        label='Bairro / Cidade',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('cpf', 'cep', 'logradouro', 'numero', 'bairro_cidade',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Consolida o endereço para salvar no modelo Perfil
        endereco_final = f"{self.cleaned_data['logradouro']}, {self.cleaned_data['numero']} - {self.cleaned_data['bairro_cidade']}"
        cpf = self.cleaned_data['cpf']
        
        Perfil.objects.update_or_create(
            user=user, 
            defaults={'cpf': cpf, 'endereco': endereco_final}
        )
        return user