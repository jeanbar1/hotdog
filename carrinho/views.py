import json
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


@login_required(login_url='loginRapido')
def carrinho(request, id=None):
    if id and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar este carrinho.')
        return redirect('carrinho')
    
    user = get_object_or_404(Usuario, id=id) if id else request.user
    carrinho_usuario, created = Carrinho.objects.get_or_create(usuario=user)
    itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario).select_related('produto').prefetch_related('adicionais')
    locais_entrega = LocalEntrega.objects.all()
    
    # Calcula os totais - MODIFICADO PARA INCLUIR ADICIONAIS
    total_produtos = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
    total_adicionais = sum(
        sum(adicional.preco_extra for adicional in item.adicionais.all()) * item.quantidade 
        for item in itens_carrinho
    )
    total_geral = total_produtos + total_adicionais  # Agora inclui os adicionais
    
    context = {
        'itens_carrinho': itens_carrinho,
        'total': total_produtos,  # Mantém como estava (sem adicionais)
        'total_adicionais': total_adicionais,  # Novo campo para mostrar adicionais separadamente
        'total_geral': total_geral,  # Total final (produtos + adicionais)
        'is_own_cart': user == request.user,
        'locais_entrega': locais_entrega,
        'total_com_entrega': total_geral  # Inicial sem taxa
    }
    return render(request, 'carrinho/carrinho.html', context)



from django.http import JsonResponse

@login_required(login_url='loginRapido')
def adicionar_ao_carrinho(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)

        if not produto.ativo:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Produto indisponível'}, status=400)
            messages.error(request, 'Este produto está indisponível.')
            return redirect('detalhes_produto', id=produto.id)

        carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)

        try:
            quantidade = int(request.POST.get('quantidade', 1))
            if quantidade < 1:
                raise ValueError("Quantidade deve ser positiva.")
            observacao = request.POST.get('observacao', '')
            adicionais_raw = request.POST.get('adicionais', '')
            adicionais_ids = [int(aid) for aid in adicionais_raw.split(',') if aid.strip().isdigit()]
            adicionais = Adicional.objects.filter(id__in=adicionais_ids)
        except (ValueError, TypeError):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Dados inválidos.'}, status=400)
            messages.error(request, 'Dados inválidos.')
            return redirect('detalhes_produto', id=produto.id)

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

        item.adicionais.set(adicionais)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, f'"{produto.nome}" adicionado ao carrinho!')
        return redirect('detalhes_produto', id=produto.id)

    return redirect('home')



@login_required(login_url='loginRapido')
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

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Temporário para testes - remova em produção
@require_POST
@login_required(login_url='loginRapido')
def atualizar_carrinho(request):
    try:
        # Obter dados do POST
        data = json.loads(request.body)
        item_id = data.get('produto_id')
        quantidade = int(data.get('quantidade'))
        
        if not item_id or quantidade < 1:
            return JsonResponse({
                'success': False,
                'message': 'Dados inválidos'
            }, status=400)

        with transaction.atomic():
            item = ItemCarrinho.objects.filter(
                id=item_id,
                carrinho__usuario=request.user
            ).first()

            if not item:
                return JsonResponse({
                    'success': False,
                    'message': 'Item não encontrado no seu carrinho'
                }, status=404)

            item.quantidade = quantidade
            item.save()

            # Calcular totais atualizados
            total_item = item.produto.preco * quantidade
            total_adicionais = sum(adicional.preco_extra for adicional in item.adicionais.all()) * quantidade
            total_geral_item = total_item + total_adicionais

            return JsonResponse({
                'success': True,
                'item_total': f'{total_item:.2f}',
                'adicionais_total': f'{total_adicionais:.2f}',
                'total_geral_item': f'{total_geral_item:.2f}',
                'quantidade': quantidade,
                'message': 'Quantidade atualizada com sucesso!'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar: {str(e)}'
        }, status=500)
        
        
        
   
    
    
    
@require_http_methods(["GET", "POST"])
@login_required
@transaction.atomic
def confirmar_compra(request):
    try:
        carrinho = get_object_or_404(Carrinho, usuario=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho)\
            .select_related('produto')\
            .prefetch_related('adicionais')
        bairros = Bairro.objects.all().order_by('nome')

        if not itens_carrinho.exists():
            messages.warning(request, 'Seu carrinho está vazio!')
            return redirect('listar_produtos')

        if request.method == "POST":
            bairro_id = request.POST.get('bairro')
            endereco = request.POST.get('endereco', '').strip()
            forma_pagamento = request.POST.get('forma_pagamento')
            precisa_troco = request.POST.get('precisa_troco') == 'on'
            valor_troco_para = request.POST.get('valor_troco_para', None)
            
            # Validação dos campos obrigatórios
            if not bairro_id or not endereco or not forma_pagamento:
                messages.error(request, 'Preencha todos os campos obrigatórios')
                return redirect('confirmar_compra')
            
            # Validação específica para pagamento em dinheiro
            if forma_pagamento == 'DINHEIRO' and precisa_troco and not valor_troco_para:
                messages.error(request, 'Informe para quanto precisa de troco')
                return redirect('confirmar_compra')

            with transaction.atomic():
                bairro = get_object_or_404(Bairro, id=bairro_id)
                
                # Criar pedido - o número diário será gerado automaticamente no save()
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    preco_total=0,  # Será atualizado após criar os itens
                    bairro_entrega=bairro,
                    endereco_entrega=endereco,
                    referencia_entrega=request.POST.get('referencia', ''),
                    forma_pagamento=forma_pagamento,
                    precisa_troco=precisa_troco,
                    valor_troco_para=valor_troco_para if forma_pagamento == 'DINHEIRO' and precisa_troco else None,
                    taxa_entrega=bairro.taxa
                )

                # Criar itens do pedido e calcular totais
                for item in itens_carrinho:
                    preco_adicionais = sum(adicional.preco_extra for adicional in item.adicionais.all())
                    preco_unitario = item.produto.preco + preco_adicionais
                    
                    item_pedido = ItemPedido.objects.create(
                        pedido=pedido,
                        produto=item.produto,
                        quantidade=item.quantidade,
                        preco_unitario=preco_unitario,
                        observacoes=item.observacao or ""
                    )
                    
                    item_pedido.adicionais.set(item.adicionais.all())
                
                # Atualizar total do pedido
                pedido.atualizar_total()
                                
                # Limpar carrinho
                itens_carrinho.delete()

            messages.success(request, f'Pedido #{pedido.numero_diario} criado com sucesso!')
            return redirect('detalhe_pedido', id=pedido.id)

        # Para GET - calcular totais para exibição
        total_produtos = sum(item.produto.preco * item.quantidade for item in itens_carrinho)
        total_adicionais = sum(
            sum(adicional.preco_extra for adicional in item.adicionais.all()) * item.quantidade
            for item in itens_carrinho
        )
        total_geral = total_produtos + total_adicionais

        return render(request, 'pedido/confirmar_pedido.html', {
            'itens': itens_carrinho,
            'total_produtos': total_produtos,
            'total_adicionais': total_adicionais,
            'total_geral': total_geral,
            'bairros': bairros,
            'formas_pagamento': Pedido.FORMA_PAGAMENTO,
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