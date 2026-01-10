from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pulseira, Perfil

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
            'condicao_medica': forms.Textarea(attrs={'rows': 3}),
            'alergias': forms.Textarea(attrs={'rows': 3}),
            'medicamentos': forms.Textarea(attrs={'rows': 3}),
            'instrucoes_abordagem': forms.Textarea(attrs={'rows': 3}),
        }

        # --- NOVO: FORMULÁRIO DE CADASTRO COM CPF ---
class CadastroUsuarioForm(UserCreationForm):
    cpf = forms.CharField(
        label='CPF', 
        max_length=14,
        widget=forms.TextInput(attrs={'placeholder': '000.000.000-00', 'class': 'form-control'})
    )
    endereco = forms.CharField(
        label='Endereço', 
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Adiciona os campos novos na lista de campos do User
        fields = UserCreationForm.Meta.fields + ('cpf', 'endereco',)

    def save(self, commit=True):
        # 1. Salva o Usuário (Nome e Senha)
        user = super().save(commit=commit)
        
        # 2. Salva o Perfil (CPF e Endereço)
        cpf = self.cleaned_data['cpf']
        endereco = self.cleaned_data['endereco']
        
        # Cria ou atualiza o perfil vinculado
        Perfil.objects.update_or_create(user=user, defaults={'cpf': cpf, 'endereco': endereco})
        
        return user