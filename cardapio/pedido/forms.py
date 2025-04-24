from django import forms
from django.forms import inlineformset_factory
from .models import *

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'status', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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