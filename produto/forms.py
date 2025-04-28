from django import forms
from django.forms import ModelForm
from .models import CategoriaProduto, Produto, Adicional, ProdutoAdicional  # Adicionei os novos modelos importados

class ProdutoForm(ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'categorias', 'preco', 'imagem', 'disponivel']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome do produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control-textarea', 'placeholder': 'Digite a descrição'}),
            'categorias': forms.CheckboxSelectMultiple(attrs={'class': 'form-control-select-multiple'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Digite o preço'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'disponivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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

# FORMULÁRIOS NOVOS (APENAS ADICIONEI A PARTIR DAQUI) --------------------------

class AdicionalForm(forms.ModelForm):
    class Meta:
        model = Adicional
        fields = ['nome', 'preco_extra', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Catupiry, Cheddar...'
            }),
            'preco_extra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'nome': 'Nome do Adicional',
            'preco_extra': 'Preço Extra',
            'ativo': 'Ativo'
        }

class ProdutoAdicionalForm(forms.ModelForm):
    class Meta:
        model = ProdutoAdicional
        fields = ['produto', 'adicional', 'ativo']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'adicional': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'produto': 'Produto',
            'adicional': 'Adicional',
            'ativo': 'Disponível'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = Produto.objects.all()
        self.fields['adicional'].queryset = Adicional.objects.filter(ativo=True)