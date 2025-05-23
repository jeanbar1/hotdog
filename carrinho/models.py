from django.db import models
from produto.models import Adicional, Produto
from usuario.models import Usuario

class Carrinho(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrinho')
    produto = models.ManyToManyField(Produto, through='ItemCarrinho')
    
    def total(self):
        total = 0
        for item in self.itens.all():
            total += item.produto.preco * item.quantidade
            for adicional in item.adicionais.all():
                total += adicional.preco_extra * item.quantidade
        return total
    
    def __str__(self):
        return f'Carrinho de {self.usuario.username}'

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    observacao = models.CharField(max_length=100, blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    adicionais = models.ManyToManyField(Adicional, blank=True)  # ← Adicionais já estava no seu código, só removi o comentário redundante

    def total_item(self):
        total = self.produto.preco * self.quantidade
        for adicional in self.adicionais.all():
            total += adicional.preco_extra * self.quantidade
        return total
    
    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome}'

# ALTERAÇÕES:
# 1. Removido o bloco de código duplicado que começava novamente com: `from django.db import models...`.
# 2. Mantido apenas um conjunto funcional de classes `Carrinho` e `ItemCarrinho`.
# 3. Comentei a linha dos adicionais para sinalizar que já estava presente corretamente.

