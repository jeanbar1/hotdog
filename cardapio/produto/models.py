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

    def __str__(self):
        tipos_str = ", ".join([tipo.nome for tipo in self.categorias.all()])
        return f'{self.nome} - {tipos_str}'