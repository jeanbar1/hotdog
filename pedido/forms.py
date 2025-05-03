from django import forms
from django.forms import inlineformset_factory
from .models import *

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'forma_pagamento', 'precisa_troco', 'valor_troco_para']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'precisa_troco': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valor_troco_para': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'forma_pagamento': 'Forma de Pagamento',
            'precisa_troco': 'Precisa de troco?',
            'valor_troco_para': 'Troco para quanto? (R$)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar o campo de troco condicional
        if not self.instance.pk or self.instance.forma_pagamento != 'DINHEIRO':
            self.fields['valor_troco_para'].required = False
            self.fields['precisa_troco'].required = False

class ItemPedidoForm(forms.ModelForm):
    adicionais = forms.ModelMultipleChoiceField(
        queryset=Adicional.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade', 'adicionais']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adicionais'].queryset = Adicional.objects.filter(ativo=True)

# Formset para múltiplos itens
ItemPedidoFormSet = inlineformset_factory(
    Pedido, 
    ItemPedido, 
    form=ItemPedidoForm,
    extra=1,
    can_delete=True
)

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