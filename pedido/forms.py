from django import forms
from django.forms import inlineformset_factory
from .models import *

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'status']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade']
        widgets = {
            'produto': forms.Select(attrs={
                'class': 'form-control select-produto',
                'data-live-search': 'true'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control quantidade',
                'min': '1'
            }),
        }

# Formset para múltiplos itens
ItemPedidoFormSet = inlineformset_factory(
    Pedido, 
    ItemPedido, 
    form=ItemPedidoForm,
    extra=1,
    can_delete=True
)





#---------------------forms entrega-----------------------




class BairroForm(forms.ModelForm):
    class Meta:
        model = Bairro
        fields = ['nome', 'taxa', 'tempo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do Bairro/Zona'
            }),
            'taxa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tempo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 30-45 min'
            }),
        }
        labels = {
            'nome': 'Nome do Bairro/Zona',
            'taxa': 'Taxa de Entrega (R$)',
            'tempo': 'Tempo Estimado de Entrega',
        }
        
        

class LocalEntregaForm(forms.ModelForm):
    class Meta:
        model = LocalEntrega
        fields = ['bairro', 'endereco']
        widgets = {
            'bairro': forms.Select(attrs={
                'class': 'form-control',
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Rua das Flores, nº 123'
            }),
        }
        labels = {
            'bairro': 'Selecione o Bairro',
            'endereco': 'Endereço Completo',
        }