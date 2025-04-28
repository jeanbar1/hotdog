from django import forms
from django.contrib.auth.forms import UserCreationForm
from jsonschema import ValidationError
from .models import Usuario

class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('nome', 'email', 'telefone', 'password1', 'password2')  # Removemos 'username'
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu melhor email'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(99) 99999-9999'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza os campos de senha
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Crie uma senha segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repita a senha'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

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

        # Se a imagem existir, valida o tamanho
        if imagem:
            # Remover a verificação de 2MB ou aumentar o limite conforme desejado
            max_size = 10 * 1024 * 1024  # 10MB
            if imagem.size > max_size:
                raise ValidationError(_('A imagem não pode ser maior que 10MB.'))

        return imagem