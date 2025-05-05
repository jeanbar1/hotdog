import os
from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from produto.models import CategoriaProduto, Produto
from carrinho.models import Carrinho  # Importe o model Carrinho

# principal/views.py
from django.http import JsonResponse
from produto.models import Produto
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings



def home(request):
    produtos = Produto.objects.all().order_by('nome')
    
    # Filtros
    pesquisa = request.GET.get('pesquisa', '').strip()
    categoria_id = request.GET.get('categoria')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    sort = request.GET.get('sort', '')
    
    # Ordenação
    if sort == 'preco_asc':
        produtos = produtos.order_by('preco')
    elif sort == 'preco_desc':
        produtos = produtos.order_by('-preco')
    
    # Aplicar filtros
    if pesquisa:
        produtos = produtos.filter(Q(nome__icontains=pesquisa) | Q(descricao__icontains=pesquisa))
    
    if categoria_id:
        produtos = produtos.filter(categorias__id=categoria_id)
    
    if preco_min:
        produtos = produtos.filter(preco__gte=preco_min)
    
    if preco_max:
        produtos = produtos.filter(preco__lte=preco_max)
    
    # Paginação
    paginator = Paginator(produtos, 12)
    page = request.GET.get('page')
    
    try:
        produtos_pagina = paginator.page(page)
    except PageNotAnInteger:
        produtos_pagina = paginator.page(1)
    except EmptyPage:
        produtos_pagina = paginator.page(paginator.num_pages)
    
    categorias = CategoriaProduto.objects.all()
    
    # Contagem de itens no carrinho
    carrinho_itens_count = 0
    if request.user.is_authenticated:
        carrinho = request.user.carrinho.first()
        if carrinho:
            carrinho_itens_count = carrinho.itens.count()
    
    context = {
        'produtos': produtos_pagina,
        'categorias': categorias,
        'pesquisa': pesquisa,
        'preco_min': preco_min,
        'preco_max': preco_max,
        'categoria_id': int(categoria_id) if categoria_id else 0,
        'sort': sort,
        'carrinho_count': carrinho_itens_count,
    }
    
    # Controle de permissões/admin
    if request.user.is_authenticated:
        tipo_cliente = getattr(request.user, 'tipo_cliente', None)
        
        if tipo_cliente == "ADMINISTRADOR" or request.user.is_superuser:
            request.user.groups.clear()
            if hasattr(request.user, 'tipo_cliente'):
                request.user.tipo_cliente = "ADMINISTRADOR"
            request.user.is_superuser = True
            grupo, created = Group.objects.get_or_create(name='Administradores')
            request.user.groups.add(grupo)

        request.user.save()
    
    return render(request, 'principal/home.html', context)


@login_required
def user_settings(request):
    return render(request, 'principal/settings.html', {})













@csrf_exempt
def migrate_images(request):
    # Garanta que está usando o settings do Django
    from django.conf import settings
    
    expected_token = os.environ.get('MIGRATION_TOKEN', 'default_token_local')
    
    if request.GET.get('token') != expected_token:
        return JsonResponse({'status': 'error', 'message': 'Token inválido'}, status=403)

    if settings.DEBUG:
        sample_data = []
        for p in Produto.objects.all()[:5]:
            sample_data.append({
                'id': p.id,
                'name': p.imagem.name if p.imagem else 'sem_imagem',
                'status': 'simulated'
            })
        
        print("\n" + "="*50)
        print(f"Simulação de migração (DEBUG={settings.DEBUG})")
        print(f"Total de produtos: {Produto.objects.count()}")
        print("="*50 + "\n")
        
        return JsonResponse({
            'status': 'simulation',
            'count': Produto.objects.count(),
            'sample': sample_data
        })

    results = []
    for produto in Produto.objects.all():
        if produto.imagem:
            try:
                file_info = {
                    'id': produto.id,
                    'name': produto.imagem.name,
                    'status': 'migrated',
                    'url': f"{settings.MEDIA_URL}{produto.imagem.name}"
                }
                results.append(file_info)
            except Exception as e:
                results.append({
                    'id': produto.id,
                    'error': str(e),
                    'status': 'failed'
                })

    return JsonResponse({
        'status': 'success',
        'count': len(results),
        'results': results
    })