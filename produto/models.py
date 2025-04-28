from django.db import models

class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.id} - {self.nome}"

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    categorias = models.ManyToManyField(CategoriaProduto, related_name='produtos')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    disponivel = models.BooleanField(default=True)  # Campo para controlar disponibilidade

    def __str__(self):
        tipos_str = ", ".join([tipo.nome for tipo in self.categorias.all()])
        return f'{self.nome} - {tipos_str}'

class Adicional(models.Model):
    nome = models.CharField(max_length=50)
    preco_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ativo = models.BooleanField(default=True)  # Para o admin controlar se está disponível

    def __str__(self):
        return f"{self.nome} (+ R${self.preco_extra})"

class ProdutoAdicional(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='adicionais')
    adicional = models.ForeignKey(Adicional, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)  # Para habilitar/desabilitar por produto

    class Meta:
        unique_together = ('produto', 'adicional')  # Evita duplicatas

    def __str__(self):
        return f"{self.produto.nome} - {self.adicional.nome}"