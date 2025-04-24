from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from produto.models import CategoriaProduto, Produto


def home(request):
    # Start with a base queryset ordered by a default field (e.g., 'nome')
    produtos = Produto.objects.all().order_by('nome')
    
    # Filtros
    pesquisa = request.GET.get('pesquisa', '').strip()
    categoria_id = request.GET.get('categoria')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    sort = request.GET.get('sort', '')
    
    # Apply sorting if specified (this will override the default ordering)
    if sort == 'preco_asc':
        produtos = produtos.order_by('preco')
    elif sort == 'preco_desc':
        produtos = produtos.order_by('-preco')
        
    # Apply filters
    if pesquisa:
        produtos = produtos.filter(Q(nome__icontains=pesquisa) | Q(descricao__icontains=pesquisa))
        
    if categoria_id:
        produtos = produtos.filter(categorias__id=categoria_id)
    
    if preco_min:
        produtos = produtos.filter(preco__gte=preco_min)
    
    if preco_max:
        produtos = produtos.filter(preco__lte=preco_max)
    
    # Paginação
    paginator = Paginator(produtos, 12)  # Mostra 12 produtos por página
    page = request.GET.get('page')
    
    try:
        produtos_pagina = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, exiba a primeira página.
        produtos_pagina = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo (por exemplo, 9999), exiba a última página de resultados.
        produtos_pagina = paginator.page(paginator.num_pages)
    
    categorias = CategoriaProduto.objects.all()
    
    context = {
        'produtos': produtos_pagina,
        'categorias': categorias,
        'pesquisa': pesquisa,
        'preco_min': preco_min,
        'preco_max': preco_max,
        'categoria_id': int(categoria_id) if categoria_id else 0,
        'sort': sort,
    }
    
    # User permissions handling
    if request.user.is_authenticated:
        # Safely check for tipo_cliente attribute
        tipo_cliente = getattr(request.user, 'tipo_cliente', None)
        
        if tipo_cliente == "ADMINISTRADOR" or request.user.is_superuser:
            request.user.groups.clear()
            # Only set tipo_cliente if the attribute exists
            if hasattr(request.user, 'tipo_cliente'):
                request.user.tipo_cliente = "ADMINISTRADOR"
            request.user.is_superuser = True
            grupo, created = Group.objects.get_or_create(name='Administradores')
            request.user.groups.add(grupo)

        
        request.user.save()
    
    return render(request, 'principal/home.html', context)


@login_required
def settings(request):
    """
    View para a página de configurações do site
    """
    return render(request, 'principal/settings.html', {})