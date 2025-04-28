from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

class Usuario(AbstractUser):
    TIPOS_CLIENTE = [
        ('CLIENTE', 'Cliente'),
        ('ADMINISTRADOR', 'Administrador'),
    ]
    
    # Campos básicos
    telefone = models.CharField(_('telefone'), max_length=15, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    nome = models.CharField(_('nome'), max_length=50, blank=True)
    
    # Tipo de cliente
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPOS_CLIENTE,
        default='CLIENTE',
    )
    
    # Imagem de perfil
    imagem = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True,
        verbose_name='Imagem de Perfil',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Removemos 'username' pois será gerado automaticamente

    def save(self, *args, **kwargs):
        """Sobrescreve o save para gerar username automaticamente e configurar grupos"""
        is_new = not self.pk
        
        # Gera username automaticamente se for um novo usuário
        if is_new:
            base_username = self.nome.lower().replace(' ', '') if self.nome else 'user'
            username = base_username
            counter = 1
            
            # Enquanto o username existir, adiciona um número no final
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
        
        super().save(*args, **kwargs)
        
        # Configura grupos baseados no tipo de cliente
        if is_new:
            if self.tipo_cliente == 'ADMINISTRADOR' or self.is_superuser:
                grupo_admin, _ = Group.objects.get_or_create(name='Administradores')
                self.groups.add(grupo_admin)
                self.is_staff = True
            else:
                grupo_clientes, _ = Group.objects.get_or_create(name='Clientes')
                self.groups.add(grupo_clientes)
                self.is_staff = False

    # ... restante do seu código ...

    def __str__(self):
        return f"{self.nome or self.username} ({self.get_tipo_cliente_display()})"

    def is_admin(self):
        return self.tipo_cliente == 'ADMINISTRADOR' or self.is_superuser
    
    def get_size_items(self):
        if hasattr(self, 'carrinho') and self.carrinho.first():
            return self.carrinho.first().itens.count()
        return 0