from django.db import models
from usuario.models import Usuario
from produto.models import Produto

class Bairro(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Bairro")
    taxa = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        verbose_name="Taxa de Entrega"
    )
    tempo = models.CharField(
        max_length=50, 
        default="30-45 min",
        verbose_name="Tempo Estimado"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Bairro"
        verbose_name_plural = "Bairros"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} (Taxa: R$ {self.taxa})"

class Pedido(models.Model):
    STATUS_PEDIDO = [
        ('PROCESSANDO', 'Processando'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='pedidos',
        verbose_name="Cliente"
    )
    bairro_entrega = models.ForeignKey(
        Bairro, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="Bairro de Entrega"
    )
    endereco_entrega = models.CharField(
        max_length=150, 
        verbose_name="Endereço Completo"
    )
    referencia_entrega = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Ponto de Referência"
    )
    taxa_entrega = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        verbose_name="Taxa de Entrega"
    )
    data_pedido = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do Pedido"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    preco_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Preço Total"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_PEDIDO, 
        default='PROCESSANDO',
        verbose_name="Status"
    )

    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.username}'

    def atualizar_total(self):
        """Atualiza o total do pedido baseado nos itens"""
        self.preco_total = sum(item.subtotal() for item in self.itens_pedido.all())
        self.save()

    def pode_ser_editado(self):
        """Verifica se o pedido ainda pode ser editado"""
        return self.status == 'PROCESSANDO'

    @property
    def total_final(self):
        """Retorna o valor total incluindo a taxa de entrega"""
        return self.preco_total + self.taxa_entrega

class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='itens_pedido',
        verbose_name="Pedido"
    )
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.PROTECT,
        verbose_name="Produto"
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade"
    )
    preco_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Preço Unitário"
    )
    observacoes = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Observações"
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} (Pedido #{self.pedido.id})'

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def save(self, *args, **kwargs):
        """Garante que o preço unitário é sempre o atual do produto"""
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)
        self.pedido.atualizar_total()

class LocalEntrega(models.Model):
    bairro = models.ForeignKey(
        Bairro, 
        on_delete=models.CASCADE,
        verbose_name="Bairro"
    )
    endereco = models.CharField(
        max_length=150, 
        verbose_name="Endereço Completo"
    )

    class Meta:
        verbose_name = "Local de Entrega"
        verbose_name_plural = "Locais de Entrega"

    def __str__(self):
        return f"{self.endereco} ({self.bairro.nome})"