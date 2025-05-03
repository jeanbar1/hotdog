from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import re

from jsonschema import ValidationError

class Usuario(AbstractUser):
    TIPOS_USUARIO = [
        ('CLIENTE', 'Cliente'),
        ('ADMINISTRADOR', 'Administrador'),
    ]
    
    # Campos básicos
    telefone = models.CharField(_('telefone'), max_length=15, blank=True, null=True, unique=True)  # Adicionei unique=True
    email = models.EmailField(_('email address'), unique=True)
    nome_completo = models.CharField(_('nome completo'), max_length=100, blank=True)
    
    # Tipo de usuário
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPOS_USUARIO,
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
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        permissions = [
            ('acesso_admin', 'Pode acessar a área administrativa'),
            ('acesso_cliente', 'Pode acessar apenas como cliente'),
        ]

    def save(self, *args, **kwargs):
        """Sobrescreve o save para configurar automaticamente"""
        is_new = not self.pk
        
        # Padroniza o formato do telefone antes de salvar (nova alteração)
        if self.telefone:
            # Remove qualquer formatação existente
            telefone_limpo = re.sub(r'\D', '', self.telefone)
            # Formata para o padrão (XX) XXXXX-XXXX
            if len(telefone_limpo) == 11:
                self.telefone = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        
        # Gera username automaticamente se não existir
        if not self.username:
            base_username = self.nome_completo.lower().replace(' ', '_') if self.nome_completo else 'user'
            self.username = self.generate_unique_username(base_username)
        
        # Configurações para novos usuários
        if is_new:
            if self.tipo_usuario == 'CLIENTE':
                self.set_unusable_password()  # Clientes podem não ter senha
            
            # Valida telefone para clientes (alterado para usar clean_telefone)
            if self.tipo_usuario == 'CLIENTE':
                self.clean_telefone()  # Chama a validação

        super().save(*args, **kwargs)
        
        # Configura grupos após salvar
        self.configure_groups()

    def generate_unique_username(self, base_username):
        """Gera um username único baseado no nome"""
        username = base_username
        counter = 1
        
        while Usuario.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username

    def configure_groups(self):
        """Configura grupos de permissão automaticamente"""
        if self.tipo_usuario == 'ADMINISTRADOR' or self.is_superuser:
            grupo_admin, _ = Group.objects.get_or_create(name='Administradores')
            self.groups.add(grupo_admin)
            self.is_staff = True
        else:
            grupo_clientes, _ = Group.objects.get_or_create(name='Clientes')
            self.groups.add(grupo_clientes)
            self.is_staff = False

    def clean_telefone(self):
        """Validação do formato do telefone (alterada para ser mais robusta)"""
        if self.tipo_usuario == 'CLIENTE' and not self.telefone:
            raise ValidationError("Clientes devem ter um telefone cadastrado")
        
        if self.telefone:
            telefone_limpo = re.sub(r'\D', '', self.telefone)
            if len(telefone_limpo) != 11:
                raise ValidationError("Telefone deve ter 11 dígitos (incluindo DDD)")
            
            # Formata o telefone para o padrão
            self.telefone = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        
        return self.telefone

    def __str__(self):
        return f"{self.nome_completo or self.email.split('@')[0]} ({self.get_tipo_usuario_display()})"

    @property
    def is_admin(self):
        return self.tipo_usuario == 'ADMINISTRADOR' or self.is_superuser
    
    def get_carrinho_count(self):
        """Retorna a quantidade de itens no carrinho"""
        if hasattr(self, 'carrinho') and self.carrinho.exists():
            return self.carrinho.first().itens.count()
        return 0