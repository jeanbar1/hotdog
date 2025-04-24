from django import forms
from django.forms import ModelForm
from .models import CategoriaProduto, Produto

class ProdutoForm(ModelForm):
    class  Meta:
        model = Produto
        fields = ['nome', 'descricao', 'categorias', 'preco', 'imagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome do produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control-textarea', 'placeholder': 'Digite a descrição'}),
            'categorias': forms.CheckboxSelectMultiple(attrs={'class': 'form-control-select-multiple'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Digite o preço'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da categoria'
            })
        }
        labels = {
            'nome': 'Nome da Categoria'
        }