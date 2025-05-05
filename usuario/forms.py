from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario
import re

class UsuarioAdminForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('nome_completo', 'email', 'telefone', 'tipo_usuario', 'password1', 'password2')
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email válido'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(99) 99999-9999'
            }),
            'tipo_usuario': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repita a senha'
        })

class UsuarioClienteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('nome_completo', 'telefone')
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(99) 99999-9999 (WhatsApp)'
            }),
        }

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not re.match(r'^\(\d{2}\)\s?\d{4,5}\-\d{4}$', telefone):
            raise ValidationError("Formato inválido. Use (DDD) XXXXX-XXXX")
        
        if Usuario.objects.filter(telefone=telefone).exists():
            raise ValidationError("Este telefone já está cadastrado")
            
        return telefone

class UsuarioImagemForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['imagem']
        widgets = {
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg, image/png'
            })
        }

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if imagem:
            # Limite de 5MB para imagens
            max_size = 5 * 1024 * 1024
            if imagem.size > max_size:
                raise ValidationError('A imagem não pode ser maior que 5MB.')
            
            # Verifica extensão (já validado pelo FileExtensionValidator)
        return imagem

class AcessoRapidoForm(forms.Form):
    nome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Como devemos chamar você?'
        })
    )
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(99) 99999-9999'
        })
    )

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not re.match(r'^\(\d{2}\)\s?\d{4,5}\-\d{4}$', telefone):
            raise ValidationError("Formato inválido. Use (DDD) XXXXX-XXXX")
        return telefone
    


class EditarPerfilSimplesForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome_completo', 'telefone']
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(DDD) 99999-9999'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['nome_completo'].widget.attrs['value'] = self.instance.nome_completo
            self.fields['telefone'].widget.attrs['value'] = self.instance.telefone

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone = re.sub(r'\D', '', telefone)  # Remove não-dígitos
            if len(telefone) != 11:
                raise forms.ValidationError("O telefone deve conter 11 dígitos (DDD + número)")
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        return telefone