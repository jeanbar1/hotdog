from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from carrinho.models import Carrinho, ItemCarrinho
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from principal.decorators import group_required
from .models import *
from .forms import *


@login_required
def detalhes_produto(request, id):
    """
    Mostra os detalhes de um produto.
    
    :param id: identificador do produto
    :return: uma renderização da página de detalhes do produto
    """
    produto = Produto.objects.filter(id=id).first()
    
    if not produto:
        return redirect('listar_produtos')
    
    return render(request, 'produto/produto.html', {'produto': produto})



def listar_produtos(request):
    """
    Mostra uma lista de todos os produtos cadastrados no sistema.
    
    Requer permissão de Administrador.
    
    :param request: Requisição do usuário.
    :return: Uma renderização da página de listagem de produtos.
    """
    produtos = Produto.objects.all()
    
    return render(request, 'produto/listar_produtos.html', {'produtos': produtos})



def listCategoria(request):
    """
    Mostra uma lista de todos os tipos de produtos cadastrados no sistema.
    
    Requer permissão de Administrador.
    """
    form_tipo = CategoriaProdutoForm()
    categorias = CategoriaProduto.objects.all()
    
    return render(request, 'produto/listCategoria.html', {
        "tipo_produto_form": form_tipo,
        "categorias": categorias
    })


@login_required
@group_required('Administradores')
def create_produto(request):
    """
    Cria um novo produto.
    
    Requer permissão de Administrador.
    
    :param request: Requisição do usuário.
    :return: Redireciona para a página de listagem de produtos.
    """
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
        else:
            return render(request, "produto/addProduto.html", {"form" : form, 'titulo': 'Criar produto'})
    else:
        form = ProdutoForm()
        return render(request, "produto/addProduto.html", {"form" : form, 'titulo': 'Criar produto'})
    

@login_required
@group_required('Administradores')
def edit_produto(request, id):
    """
    Edita um produto existente.

    Requer permissão de Administrador.

    :param request: Requisição do usuário.
    :param id: Id do produto a ser editado.
    :return: Redireciona para a página de listagem de produtos.
    """
    produto = Produto.objects.get(pk = id)
    print(produto)

    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto)

        if form.is_valid():
            form.save()

            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)
    
    context = {'form' : form, 'titulo' : 'Editar produto'}
    
    if produto.imagem and hasattr(produto.imagem, 'url'):
        context['current_image_url'] = produto.imagem.url
    
    return render(request, 'produto/editProduto.html', context)
    

@login_required
@group_required('Administradores')
def remove_produto(request, id):
    """
    Remove um produto existente.

    Requer permissão de Administrador.

    :param request: Requisição do usuário.
    :param id: Id do produto a ser deletado.
    :return: Redireciona para a página de listagem de produtos.
    """
    produto = Produto.objects.filter(pk = id)
    
    if produto: produto.delete()

    return redirect('listar_produtos')



@login_required
@group_required('Administradores')
def addCategoria(request):
    """
    Cria um novo tipo de produto.

    Requer permissão de Administrador.

    :param request: Requisição do usuário.
    :return: Redireciona para a página de listagem de tipos de produtos.
    """
    if request.method == "POST":
        form = CategoriaProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("listCategoria")
    else:
        form = CategoriaProdutoForm()
    
    return render(request, "produto/addCategoria.html", {"form": form, "titulo": "Criar Categoria"})
    

@login_required
@group_required('Administradores')
def editCategoria(request, id):
    """
    Edita um tipo de produto pelo id.

    Requer permissão de Administrador.

    :param request: Requisição do usuário.
    :param id: Id do tipo de produto a ser editado.
    :return: Redireciona para a página de listagem de tipos de produtos.
    """
    categoriaProduto = CategoriaProduto.objects.get(pk = id)
    print(categoriaProduto)

    if request.method == "POST":
        form = CategoriaProdutoForm(request.POST, instance=categoriaProduto)

        if form.is_valid():
            form.save()
            
            return redirect('listCategoria')
    else:
        form = CategoriaProdutoForm(instance=categoriaProduto)

    return render(request, "produto/editCategoria.html", {'form' : form, 'titulo': 'Editar tipo de produto'})


@login_required
@group_required('Administradores')
def deleteCategoria(request, id):
    categoria = get_object_or_404(CategoriaProduto, id=id)
    
    if request.method == "POST":
        # Limpa todas as mensagens antigas
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = True
        
        try:
            categoria.delete()
            messages.success(request, f'Categoria "{categoria.nome}" excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir categoria: {str(e)}')
        
        return redirect('listCategoria')
    
    return redirect('listCategoria')

def pesquisar_produtos(request):
    """
    Mostra a lista de produtos filtrados por nome, descriço, categoria, preco, tamanho e ordenados por preco.
    
    :param request: Requisição do usuário.
    :return: Retorna a página de listagem de produtos.
    """
    produtos = Produto.objects.all()
    
    # Filtros
    pesquisa = request.GET.get('pesquisa', '').strip()
    categoria_id = request.GET.get('categoria')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    sort = request.GET.get('sort', '')
    
    if sort == 'preco_asc':
        produtos = produtos.order_by('preco')
    elif sort == 'preco_desc':
        produtos = produtos.order_by('-preco')
        
    if pesquisa:
        produtos = produtos.filter(Q(nome__icontains=pesquisa) | Q(descricao__icontains=pesquisa))
        
    if categoria_id:
        produtos = produtos.filter(categorias__id=categoria_id)
    
    if preco_min:
        produtos = produtos.filter(preco__gte=preco_min)
    
    if preco_max:
        produtos = produtos.filter(preco__lte=preco_max)
    
    # Paginação
    paginator = Paginator(produtos, 12)  # Mostra 10 produtos por página
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
        'categoria_id': int(categoria_id if categoria_id else 0),
        'sort': sort,
    }
    return render(request, 'produto/pesquisa.html', context)



