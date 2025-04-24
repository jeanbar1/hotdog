from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.db import transaction

from pedido.models import Pedido, ItemPedido
from produto.models import Produto
from usuario.models import Usuario
from .models import Carrinho, ItemCarrinho


@login_required
def carrinho(request, id=None):
    """
    View para exibir o carrinho do usuário.
    Admin pode visualizar carrinho de outros usuários.
    """
    if id and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar este carrinho.')
        return redirect('carrinho')
    
    user = get_object_or_404(Usuario, id=id) if id else request.user
    carrinho_usuario, created = Carrinho.objects.get_or_create(usuario=user)
    itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario).select_related('produto')
    
    context = {
        'itens_carrinho': itens_carrinho,
        'total': carrinho_usuario.total(),
        'is_own_cart': user == request.user
    }
    return render(request, 'carrinho/carrinho.html', context)


@login_required
def remover_do_carrinho(request, id):
    """
    Remove um produto do carrinho do usuário.
    """
    produto = get_object_or_404(Produto, id=id)
    carrinho = get_object_or_404(Carrinho, usuario=request.user)
    
    item_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho, produto=produto).first()
    if item_carrinho:
        item_carrinho.delete()
        messages.success(request, f'Produto removido do carrinho.')
    
    return redirect('carrinho')


@login_required
def adicionar_ao_carrinho(request, id):
    """
    Adiciona um produto ao carrinho do usuário.
    """
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=id)
        carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
        
        quantidade = int(request.POST.get('quantidade', 1))
        
        item, created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho, 
            produto=produto,
            defaults={'quantidade': quantidade}
        )

        if not created:
            item.quantidade += quantidade
            item.save()

        messages.success(request, f'"{produto.nome}" foi adicionado ao seu carrinho!', extra_tags='carrinho')
        return redirect('listar_produtos')
    
    return redirect('listar_produtos')


@require_POST
@login_required
def atualizar_carrinho(request):
    """
    Atualiza quantidades de múltiplos itens no carrinho.
    """
    updates = {}
    for key, value in request.POST.items():
        if key.startswith('quantidade_'):
            try:
                item_id = int(key.split('_')[1])
                quantidade = int(value)
                if quantidade > 0:
                    updates[item_id] = quantidade
            except (ValueError, IndexError):
                continue
    
    if not updates:
        messages.error(request, "Nenhuma quantidade válida foi enviada.")
        return redirect('carrinho')
    
    with transaction.atomic():
        user_items = ItemCarrinho.objects.filter(
            id__in=updates.keys(),
            carrinho__usuario=request.user
        )
        
        if user_items.count() != len(updates):
            messages.error(request, "Alguns itens não pertencem ao seu carrinho.")
            return redirect('carrinho')
        
        for item in user_items:
            item.quantidade = updates[item.id]
            item.save()
    
    messages.success(request, 'Carrinho atualizado com sucesso!')
    return redirect('carrinho')


@require_http_methods(["GET", "POST"])
@login_required
@transaction.atomic
def confirmar_compra(request):
    """
    View para confirmar e finalizar a compra.
    GET: Mostra página de confirmação
    POST: Processa a finalização da compra
    """
    try:
        carrinho = get_object_or_404(Carrinho, usuario=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(
            carrinho=carrinho
        ).select_related('produto')
        
        if not itens_carrinho.exists():
            messages.warning(request, 'Seu carrinho está vazio!')
            return redirect('listar_produtos')
        
        if request.method == "POST":
            # Cria o pedido
            pedido = Pedido.objects.create(
                cliente=request.user,
                preco_total=carrinho.total(),
                status='PROCESSANDO'
            )
            
            # Cria os itens do pedido
            for item in itens_carrinho:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item.produto,
                    quantidade=item.quantidade,
                    preco=item.produto.preco
                )
            
            # Limpa o carrinho
            itens_carrinho.delete()
            
            # Adiciona mensagem de sucesso com ID do pedido
            messages.success(
                request, 
                f'Compra finalizada com sucesso! Número do pedido: #{pedido.id}'
            )
            return redirect('detalhe_pedido', id=pedido.id)
        
        # Método GET - mostra página de confirmação
        context = {
            'itens_carrinho': itens_carrinho,
            'total': carrinho.total(),
        }
        return render(request, 'carrinho/confirmar_compra.html', context)
    
    except Exception as e:
        # Log do erro (em produção, use logging)
        print(f"Erro ao processar pedido: {str(e)}")
        messages.error(
            request, 
            'Ocorreu um erro ao processar seu pedido. Por favor, tente novamente.'
        )
        return redirect('carrinho')

@login_required
def carrinho_count(request):
    """
    Retorna a quantidade de itens no carrinho (usada para AJAX)
    """
    count = ItemCarrinho.objects.filter(carrinho__usuario=request.user).count()
    return JsonResponse({'count': count})