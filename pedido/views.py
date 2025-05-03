from venv import logger
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from principal.decorators import group_required
from produto.models import Adicional
from .models import Bairro,LocalEntrega, Pedido, ItemPedido, Usuario
from carrinho.models import Carrinho, ItemCarrinho
from .forms import BairroForm, LocalEntregaForm, PedidoForm, ItemPedidoForm
from django.db.models import Q  # Para buscas complexas
from django.core.paginator import Paginator  # Para paginaç

@login_required(login_url='loginRapido')
def listar_pedidos(request, id=None):
    """
    Lista pedidos com controle de acesso aprimorado.
    """
    try:
        # Inicializa variáveis
        status_filter = request.GET.get('status', '')
        search_query = request.GET.get('q', '')
        
        # Base query
        if request.user.is_superuser:
            pedidos = Pedido.objects.all().select_related('cliente')
        else:
            pedidos = Pedido.objects.filter(cliente=request.user).select_related('cliente')
        
        # Aplica filtros
        if status_filter:
            pedidos = pedidos.filter(status=status_filter)
        
        if search_query:
            pedidos = pedidos.filter(
                Q(id__icontains=search_query) |
                Q(cliente__username__icontains=search_query) |
                Q(cliente__first_name__icontains=search_query) |
                Q(cliente__last_name__icontains=search_query) |
                Q(endereco_entrega__icontains=search_query)
            )
        
        # Ordenação
        pedidos = pedidos.order_by('-data_pedido')
        
        # Paginação
        paginator = Paginator(pedidos, 10)  # 10 itens por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'pedido/listPedido.html', {
            'page_obj': page_obj,
            'titulo': 'Todos os Pedidos' if request.user.is_superuser else 'Meus Pedidos',
            'status_filter': status_filter,
            'search_query': search_query
        })
        
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao listar os pedidos: {str(e)}')
        return redirect('home')

@login_required
@group_required('Administradores')
def create_pedido(request):
    ItemPedidoFormSet = inlineformset_factory(
        Pedido, 
        ItemPedido, 
        form=ItemPedidoForm, 
        extra=1,
        can_delete=True
    )

    if request.method == "POST":
        form = PedidoForm(request.POST)
        formset = ItemPedidoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            pedido_data = form.cleaned_data
            item_data = []
            for form_item in formset.forms:
                item = form_item.cleaned_data
                item_data.append(item)

            messages.success(request, 'Os dados foram coletados com sucesso! Veja abaixo: ')
            return render(request, 'pedido/pedido_preview.html', {
                'pedido_data': pedido_data,
                'item_data': item_data,
                'titulo': 'Pré-visualização do Pedido'
            })

    else:
        form = PedidoForm()
        formset = ItemPedidoFormSet()

    return render(request, 'pedido/pedido_form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Criar Novo Pedido'
    })
    
@login_required
def edit_pedido(request, id):
    """
    Edita um pedido existente (apenas para administradores).
    ATUALIZADO: Removida referência ao status e adicionados campos de pagamento
    """
    pedido = get_object_or_404(Pedido, pk=id)
    
    if not pedido.pode_ser_editado():
        messages.error(request, 'Este pedido não pode mais ser editado.')
        return redirect('detalhe_pedido', id=pedido.numero_diario)
    
    ItemPedidoFormSet = inlineformset_factory(
        Pedido, ItemPedido, form=ItemPedidoForm, extra=1, can_delete=True
    )
    
    if request.method == "POST":
        form = PedidoForm(request.POST, instance=pedido)
        formset = ItemPedidoFormSet(request.POST, instance=pedido)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()
                    pedido.atualizar_total()
                    
                    messages.success(request, 'Pedido atualizado com sucesso!')
                    return redirect('detalhe_pedido', id=pedido.id)
                    
            except Exception as e:
                messages.error(request, f'Erro ao atualizar pedido: {str(e)}')
                
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            
    else:
        form = PedidoForm(instance=pedido)
        formset = ItemPedidoFormSet(instance=pedido)

    return render(request, 'pedido/editPedido.html', {
        'form': form,
        'formset': formset,
        'pedido': pedido,
        'titulo': 'Editar Pedido'
    })

@login_required
def remove_pedido(request, id):
    """
    Remove um pedido (apenas para administradores).
    """
    pedido = get_object_or_404(Pedido, pk=id)
    
    try:
        with transaction.atomic():
            if not pedido.pode_ser_editado():
                messages.error(request, 'Este pedido não pode mais ser removido.')
                return redirect('detalhe_pedido', id=pedido.id)
                
            pedido.delete()
            messages.success(request, 'Pedido removido com sucesso!')
            
    except Exception as e:
        messages.error(request, f'Erro ao remover pedido: {str(e)}')
        
    return redirect('listar_pedidos')

@login_required(login_url='loginRapido')
def detalhe_pedido(request, id):
    """
    Exibe os detalhes de um pedido específico.
    ATUALIZADO: Agora mostra os detalhes de pagamento (forma de pagamento e troco)
    """
    pedido = get_object_or_404(Pedido, pk=id)
    
    if not request.user.is_superuser and request.user.pk != pedido.cliente.pk:
        messages.error(request, 'Você não tem permissão para visualizar este pedido.')
        return redirect('listar_pedidos')
    
    itens = ItemPedido.objects.filter(pedido=pedido).select_related('produto')
    
    return render(request, 'pedido/detalhe_pedido.html', {
        'pedido': pedido,
        'itens': itens,
        'titulo': f'Pedido #{pedido.numero_diario}'
    })

# Função para verificar se o usuário é admin/staff
def is_admin(user):
    return user.is_authenticated and user.is_staff

# ----- CRUD de Bairro (nome, taxa, tempo) -----

@user_passes_test(is_admin)
def listar_bairros(request):
    bairros = Bairro.objects.all().order_by('nome')
    return render(request, 'admin/listar_bairros.html', {'bairros': bairros})

@user_passes_test(is_admin)
def adicionar_bairro(request):
    if request.method == 'POST':
        form = BairroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bairro adicionado com sucesso!')
            return redirect('listar_bairros')
    else:
        form = BairroForm()
    return render(request, 'admin/adicionar_bairro.html', {'form': form})

@user_passes_test(is_admin)
def editar_bairro(request, bairro_id):
    bairro = get_object_or_404(Bairro, id=bairro_id)
    
    if request.method == 'POST':
        form = BairroForm(request.POST, instance=bairro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bairro atualizado com sucesso!')
            return redirect('listar_bairros')
    else:
        form = BairroForm(instance=bairro)
    
    return render(request, 'admin/editar_bairro.html', {'form': form, 'bairro': bairro})

@user_passes_test(is_admin)
def remover_bairro(request, bairro_id):
    bairro = get_object_or_404(Bairro, id=bairro_id)
    bairro.delete()
    messages.success(request, 'Bairro removido com sucesso!')
    return redirect('listar_bairros')

# ----- CRUD de LocalEntrega (bairro + endereço completo) -----

@user_passes_test(is_admin)
def listar_enderecos(request):
    enderecos = LocalEntrega.objects.select_related('bairro').all().order_by('endereco')
    return render(request, 'admin/listar_enderecos.html', {'enderecos': enderecos})

@user_passes_test(is_admin)
def adicionar_endereco(request):
    if request.method == 'POST':
        form = LocalEntregaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Endereço adicionado com sucesso!')
            return redirect('listar_enderecos')
    else:
        form = LocalEntregaForm()
    return render(request, 'admin/adicionar_endereco.html', {'form': form})

@user_passes_test(is_admin)
def editar_endereco(request, endereco_id):
    endereco = get_object_or_404(LocalEntrega, id=endereco_id)
    
    if request.method == 'POST':
        form = LocalEntregaForm(request.POST, instance=endereco)
        if form.is_valid():
            form.save()
            messages.success(request, 'Endereço atualizado com sucesso!')
            return redirect('listar_enderecos')
    else:
        form = LocalEntregaForm(instance=endereco)
    
    return render(request, 'admin/editar_endereco.html', {'form': form, 'endereco': endereco})

@user_passes_test(is_admin)
def remover_endereco(request, endereco_id):
    endereco = get_object_or_404(LocalEntrega, id=endereco_id)
    endereco.delete()
    messages.success(request, 'Endereço removido com sucesso!')
    return redirect('listar_enderecos')


@login_required
def criar_pedido_do_carrinho(request):
    """
    Cria um pedido a partir do carrinho de compras.
    Agora atribui automaticamente um número diário reiniciado por dia.
    """
    try:
        carrinho = Carrinho.objects.get(usuario=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho).prefetch_related('adicionais')

        if request.method == 'POST':
            form = PedidoForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        pedido = form.save(commit=False)
                        pedido.cliente = request.user

                        # Gerar número diário
                        hoje = timezone.now().date()
                        ultimo_pedido_hoje = Pedido.objects.filter(data_criacao=hoje).order_by('-numero_diario').first()
                        proximo_numero = 1 if not ultimo_pedido_hoje else ultimo_pedido_hoje.numero_diario + 1
                        pedido.numero_diario = proximo_numero

                        pedido.save()

                        for item_carrinho in itens_carrinho:
                            adicionais = item_carrinho.adicionais.all()
                            preco_adicionais = sum(a.preco_extra for a in adicionais)
                            preco_unitario = item_carrinho.produto.preco + preco_adicionais

                            item_pedido = ItemPedido.objects.create(
                                pedido=pedido,
                                produto=item_carrinho.produto,
                                quantidade=item_carrinho.quantidade,
                                preco_unitario=preco_unitario
                            )
                            item_pedido.adicionais.set(adicionais)

                        pedido.atualizar_total()
                        carrinho.itens.all().delete()

                        messages.success(request, f'Pedido #{pedido.numero_diario} criado com sucesso!')
                        return redirect('detalhe_pedido', id=pedido.numero_diario)

                except Exception as e:
                    messages.error(request, f'Erro ao criar pedido: {str(e)}')

        else:
            form = PedidoForm()

        return render(request, 'pedido/pedido_form.html', {
            'form': form,
            'itens_carrinho': itens_carrinho,
            'titulo': 'Finalizar Pedido'
        })

    except Carrinho.DoesNotExist:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('listar_produtos')
    
    
    
    


def check_novos_pedidos(request):
    ultimo_id = int(request.GET.get('ultimo_id', 0))
    
    # Verifica se existe algum pedido mais recente que o último ID conhecido
    novo_pedido = Pedido.objects.filter(id__gt=ultimo_id).exists()
    
    # Obtém o ID do pedido mais recente
    ultimo_id_atual = Pedido.objects.order_by('-id').values_list('id', flat=True).first() or 0
    
    return JsonResponse({
        'novo_pedido': novo_pedido,
        'ultimo_id': ultimo_id_atual
    })