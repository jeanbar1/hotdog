from django.db import models
from produto.models import Produto
from usuario.models import Usuario

class Carrinho(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrinho')
    produto = models.ManyToManyField(Produto, through='ItemCarrinho')
    
    def total(self):
        # Calcula o total do carrinho somando o preço dos produtos multiplicado pela quantidade
        return sum(item.produto.preco * item.quantidade for item in self.itens.all())
    
    def __str__(self):
        return f'Carrinho de {self.usuario.username}'


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome}'
