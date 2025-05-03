from django.db import models
from usuario.models import Usuario
from produto.models import Adicional, Produto
from datetime import date, timedelta
from django.utils import timezone

class Bairro(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Bairro")
    taxa = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Taxa de Entrega")
    tempo = models.CharField(max_length=50, default="30-45 min", verbose_name="Tempo Estimado")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Bairro"
        verbose_name_plural = "Bairros"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} (Taxa: R$ {self.taxa})"

class Pedido(models.Model):
    # FORMAS DE PAGAMENTO (NOVO - substituindo o status)
    FORMA_PAGAMENTO = [
        ('CREDITO', 'Cartão de Crédito'),
        ('DEBITO', 'Cartão de Débito'),
        ('PIX', 'PIX'),
        ('DINHEIRO', 'Dinheiro'),
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos', verbose_name="Cliente")
    bairro_entrega = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bairro de Entrega")
    endereco_entrega = models.CharField(max_length=150, verbose_name="Endereço Completo")
    referencia_entrega = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ponto de Referência")
    taxa_entrega = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Taxa de Entrega")
    data_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Data do Pedido")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Preço Total")
    
    # CAMPOS DE PAGAMENTO (SUBSTITUINDO O STATUS)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO, verbose_name="Forma de Pagamento")
    precisa_troco = models.BooleanField(default=False, verbose_name="Precisa de Troco?")
    valor_troco_para = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Troco para (R$)")

    numero_diario = models.PositiveIntegerField(default=1, verbose_name="Número do Pedido do Dia")
    data_referencia = models.DateField(default=date.today, verbose_name="Data de Referência")

    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def pode_ser_editado(self):
        """Permite edição apenas se o pedido tiver menos de 30 minutos."""
        agora = timezone.now()
        return (agora - self.data_pedido).total_seconds() < 1800

    def __str__(self):
        return f'Pedido {self.numero_diario} - {self.cliente.username} ({self.data_referencia})'

    def save(self, *args, **kwargs):
        hoje = date.today()

        if not self.pk:
            ultimo_pedido_hoje = Pedido.objects.filter(data_referencia=hoje).order_by('-numero_diario').first()
            if ultimo_pedido_hoje:
                self.numero_diario = ultimo_pedido_hoje.numero_diario + 1
            else:
                self.numero_diario = 1
            self.data_referencia = hoje

        super().save(*args, **kwargs)

    def atualizar_total(self):
        self.preco_total = sum(item.subtotal for item in self.itens_pedido.all())
        if self.bairro_entrega:
            self.taxa_entrega = self.bairro_entrega.taxa
        self.save()
        
    def pode_ser_editado(self):
        """Verifica se o pedido pode ser editado/removido (dentro de 5 minutos da criação)"""
        tempo_decorrido = (timezone.now() - self.data_pedido).total_seconds()
        return tempo_decorrido < 300  # 5 minutos = 300 segundos
    
    def pode_ser_removido(self):
        """Verifica se o pedido pode ser removido (dentro de 5 minutos da criação)"""
        tempo_decorrido = (timezone.now() - self.data_pedido).total_seconds()
        return tempo_decorrido < 300  # 5 minutos = 300 segundos
    
    def save(self, *args, **kwargs):
        if not self.numero_diario:
            self.numero_diario = self.get_next_numero_diario()
        super().save(*args, **kwargs)

    @classmethod
    def get_next_numero_diario(cls):
        agora = timezone.localtime()
        
        # Define o horário de corte como meio-dia (12:00)
        if agora.hour < 12:
            inicio_dia = agora.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=1)
        else:
            inicio_dia = agora.replace(hour=12, minute=0, second=0, microsecond=0)

        # Conta quantos pedidos existem a partir do início do "dia lógico"
        count = cls.objects.filter(data_criacao__gte=inicio_dia).count()
        return count + 1

    @property
    def subtotal_produtos(self):
        return sum(item.total_produto for item in self.itens_pedido.all())

    @property
    def total_adicionais(self):
        return sum(item.adicionais_total for item in self.itens_pedido.all())

    @property
    def total_final(self):
        return self.subtotal_produtos + self.total_adicionais + self.taxa_entrega

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens_pedido', verbose_name="Pedido")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, verbose_name="Produto")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    observacoes = models.CharField(max_length=100, blank=True, null=True, verbose_name="Observações")
    adicionais = models.ManyToManyField(Adicional, blank=True)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} (Pedido #{self.pedido.id})'

    @property
    def adicionais_total(self):
        return sum(adicional.preco_extra for adicional in self.adicionais.all()) * self.quantidade

    @property
    def total_produto(self):
        return self.preco_unitario * self.quantidade

    @property
    def subtotal(self):
        return self.total_produto + self.adicionais_total

    def save(self, *args, **kwargs):
        if not self.pk or not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)
        self.pedido.atualizar_total()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        super().delete(*args, **kwargs)
        pedido.atualizar_total()

class LocalEntrega(models.Model):
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, verbose_name="Bairro")
    endereco = models.CharField(max_length=150, verbose_name="Endereço Completo")

    class Meta:
        verbose_name = "Local de Entrega"
        verbose_name_plural = "Locais de Entrega"

    def __str__(self):
        return f"{self.endereco} ({self.bairro.nome})"
    
    
    
    