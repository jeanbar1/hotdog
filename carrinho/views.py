from venv import logger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.db import transaction
from jsonschema import ValidationError

from pedido.models import Bairro, Pedido, ItemPedido, LocalEntrega
from produto.models import Adicional, Produto
from usuario.models import Usuario
from .models import Carrinho, ItemCarrinho



@login_required
def carrinho(request, id=None):
    if id and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar este carrinho.')
        return redirect('carrinho')
    
    user = get_object_or_404(Usuario, id=id) if id else request.user
    carrinho_usuario, created = Carrinho.objects.get_or_create(usuario=user)
    itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario).select_related('produto').prefetch_related('adicionais')
    locais_entrega = LocalEntrega.objects.all()
    
    # Calcula os totais
    total_produtos = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
    total_adicionais = sum(
        sum(adicional.preco_extra for adicional in item.adicionais.all()) * item.quantidade 
        for item in itens_carrinho
    )
    total_geral = total_produtos + total_adicionais
    
    context = {
        'itens_carrinho': itens_carrinho,
        'total': total_produtos,
        'total_adicionais': total_adicionais,
        'total_geral': total_geral,
        'is_own_cart': user == request.user,
        'locais_entrega': locais_entrega,
        'total_com_entrega': total_geral  # Inicial sem taxa
    }
    return render(request, 'carrinho/carrinho.html', context)

@login_required
def adicionar_ao_carrinho(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)
        carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
        
        try:
            quantidade = int(request.POST.get('quantidade', 1))
            if quantidade < 1:
                raise ValueError
            observacao = request.POST.get('observacao', '')
            adicionais_ids = request.POST.get('adicionais', '').split(',')
            adicionais = Adicional.objects.filter(id__in=adicionais_ids)
        except (ValueError, TypeError):
            messages.error(request, 'Quantidade inválida.')
            return redirect('detalhes_produto', id=produto.id)

        # Cria ou atualiza o item no carrinho
        item, created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={
                'quantidade': quantidade,
                'observacao': observacao
            }
        )

        if not created:
            item.quantidade += quantidade
            if observacao:
                item.observacao = observacao
            item.save()
        
        # Adiciona os adicionais ao item
        item.adicionais.clear()
        for adicional in adicionais:
            item.adicionais.add(adicional)

        messages.success(request, f'"{produto.nome}" adicionado ao carrinho!')
        return redirect('detalhes_produto', id=produto.id)
    
    return redirect('home')

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
    try:
        carrinho = get_object_or_404(Carrinho, usuario=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho).select_related('produto')
        bairros = Bairro.objects.all().order_by('nome')

        if not itens_carrinho.exists():
            messages.warning(request, 'Seu carrinho está vazio!')
            return redirect('listar_produtos')

        if request.method == "POST":
            bairro_id = request.POST.get('bairro')
            endereco = request.POST.get('endereco', '').strip()
            
            if not bairro_id or not endereco:
                messages.error(request, 'Preencha todos os campos obrigatórios')
                return redirect('confirmar_compra')

            with transaction.atomic():
                # Criar pedido
                bairro = get_object_or_404(Bairro, id=bairro_id)
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    preco_total=carrinho.total() + bairro.taxa,
                    bairro_entrega=bairro,
                    endereco_entrega=endereco,
                    referencia_entrega=request.POST.get('referencia', ''),
                    status='PROCESSANDO',
                    taxa_entrega=bairro.taxa
                )

                # Criar itens garantindo todos os campos obrigatórios
                for item in itens_carrinho:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto=item.produto,
                        quantidade=item.quantidade,
                        preco_unitario=item.produto.preco,  # Campo obrigatório
                        observacoes=item.observacao or ""
                    )

                itens_carrinho.delete()

            messages.success(request, f'Pedido #{pedido.id} criado com sucesso!')
            return redirect('detalhe_pedido', id=pedido.id)

        return render(request, 'pedido/confirmar_pedido.html', {
            'itens': itens_carrinho,
            'total': carrinho.total(),
            'bairros': bairros,
        })

    except Exception as e:
        logger.error(f"Erro na confirmação: {str(e)}", exc_info=True)
        messages.error(request, 'Erro ao processar seu pedido')
        return redirect('carrinho')

@login_required
def calcular_taxa(request):
    """
    View AJAX para cálculo em tempo real da taxa de entrega
    Retorna JSON com: taxa, total_com_taxa e tempo_entrega
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Requisição inválida'}, status=400)

    try:
        bairro_id = request.GET.get('bairro_id')
        subtotal = float(request.GET.get('total', 0))
        
        if not bairro_id:
            return JsonResponse({'error': 'Bairro não selecionado'}, status=400)

        bairro = Bairro.objects.get(id=bairro_id)
        taxa = float(bairro.taxa)
        
        return JsonResponse({
            'taxa': taxa,
            'total_com_taxa': subtotal + taxa,
            'tempo_entrega': bairro.tempo,
            'taxa_formatada': f'R$ {taxa:.2f}',
            'total_formatado': f'R$ {subtotal + taxa:.2f}'
        })

    except Bairro.DoesNotExist:
        return JsonResponse({'error': 'Bairro não encontrado'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Valores inválidos'}, status=400)
    except Exception as e:
        logger.error(f"Erro no cálculo de taxa: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro no servidor'}, status=500)




@login_required
def carrinho_count(request):
    """
    Retorna a quantidade de itens no carrinho (usada para AJAX)
    """
    count = ItemCarrinho.objects.filter(carrinho__usuario=request.user).count()
    return JsonResponse({'count': count})