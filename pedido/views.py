from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import Http404
from django.contrib.auth.decorators import user_passes_test
from principal.decorators import group_required
from .models import Bairro, LocalEntrega, Pedido, ItemPedido, Usuario
from carrinho.models import Carrinho, ItemCarrinho
from .forms import BairroForm, LocalEntregaForm, PedidoForm, ItemPedidoForm

@login_required
def listar_pedidos(request, id=None):
    """
    Lista pedidos com controle de acesso aprimorado.
    
    Args:
        request: HttpRequest object
        id: ID do usuário (opcional) - se fornecido, lista pedidos desse usuário
    
    Returns:
        HttpResponse com template renderizado
    """
    try:
        # Se um ID foi fornecido
        if id:
            # Verifica se o usuário tem permissão para ver esses pedidos
            if not request.user.is_superuser and int(id) != request.user.pk:
                messages.warning(request, 'Você só pode ver seus próprios pedidos.')
                return redirect('listar_pedidos', request.user.pk)
            
            user = get_object_or_404(Usuario, pk=id)
            pedidos = Pedido.objects.filter(cliente=user).select_related('cliente')
            
        # Se for superusuário, mostra todos os pedidos
        elif request.user.is_superuser:
            pedidos = Pedido.objects.all().select_related('cliente')
            
        # Usuário normal sem ID - redireciona para seus próprios pedidos
        else:
            return redirect('listar_pedidos', request.user.pk)
        
        # Ordena por data mais recente primeiro
        pedidos = pedidos.order_by('-data_pedido')
        
        return render(request, 'pedido/listPedido.html', {
            'pedidos': pedidos,
            'titulo': 'Meus Pedidos' if not request.user.is_superuser else 'Todos os Pedidos'
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
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    pedido.save()
                    
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.pedido = pedido
                        instance.preco_unitario = instance.produto.preco  # Define o preço automaticamente
                        instance.save()
                    
                    pedido.atualizar_total()
                    messages.success(request, 'Pedido criado com sucesso!')
                    return redirect('detalhe_pedido', id=pedido.id)
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar pedido: {str(e)}')
    else:
        form = PedidoForm()
        formset = ItemPedidoFormSet()

    return render(request, 'pedido/pedido_form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Criar Novo Pedido'
    })

@login_required
@group_required('Administradores')
def edit_pedido(request, id):
    """
    Edita um pedido existente (apenas para administradores).
    """
    pedido = get_object_or_404(Pedido, pk=id)
    
    # Verifica se o pedido pode ser editado
    if not pedido.pode_ser_editado():
        messages.error(request, 'Este pedido não pode mais ser editado.')
        return redirect('detalhe_pedido', id=pedido.id)
    
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
@group_required('Administradores')
def remove_pedido(request, id):
    """
    Remove um pedido (apenas para administradores).
    """
    pedido = get_object_or_404(Pedido, pk=id)
    
    try:
        with transaction.atomic():
            # Verifica se o pedido pode ser removido
            if not pedido.pode_ser_editado():
                messages.error(request, 'Este pedido não pode mais ser removido.')
                return redirect('detalhe_pedido', id=pedido.id)
                
            pedido.delete()
            messages.success(request, 'Pedido removido com sucesso!')
            
    except Exception as e:
        messages.error(request, f'Erro ao remover pedido: {str(e)}')
        
    return redirect('listar_pedidos')

@login_required
def detalhe_pedido(request, id):
    """
    Exibe os detalhes de um pedido específico.
    O usuário só pode ver seus próprios pedidos, a menos que seja administrador.
    """
    pedido = get_object_or_404(Pedido, pk=id)
    
    # Verifica permissão
    if not request.user.is_superuser and request.user.pk != pedido.cliente.pk:
        messages.error(request, 'Você não tem permissão para visualizar este pedido.')
        return redirect('listar_pedidos')
    
    itens = ItemPedido.objects.filter(pedido=pedido).select_related('produto')
    
    return render(request, 'pedido/detalhe_pedido.html', {
        'pedido': pedido,
        'itens': itens,
        'titulo': f'Pedido #{pedido.id}'
    })

@login_required
def criar_pedido_do_carrinho(request):
    carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho).select_related('produto')
    
    if not itens_carrinho.exists():
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('carrinho')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Cria o pedido
                    pedido = form.save(commit=False)
                    pedido.cliente = request.user
                    pedido.status = 'PROCESSANDO'
                    pedido.save()
                    
                    # Transferência dos itens com verificação explícita
                    for item_carrinho in itens_carrinho:
                        # Garante que a observação não seja None
                        obs = item_carrinho.observacao if item_carrinho.observacao else ""
                        
                        # Cria o item do pedido com todos os campos
                        ItemPedido.objects.create(
                            pedido=pedido,
                            produto=item_carrinho.produto,
                            quantidade=item_carrinho.quantidade,
                            preco_unitario=item_carrinho.produto.preco,
                            observacoes=obs,  # Campo exatamente como no modelo
                        )
                    
                    # Limpa o carrinho
                    itens_carrinho.delete()
                    pedido.atualizar_total()
                    
                    messages.success(request, f'Pedido #{pedido.id} criado com sucesso!')
                    return redirect('detalhe_pedido', id=pedido.id)
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar pedido: {str(e)}')
                return redirect('carrinho')
    else:
        form = PedidoForm(initial={'cliente': request.user})
    
    # Cálculo do resumo do pedido
    itens_resumo = [
        {
            'produto': item.produto,
            'quantidade': item.quantidade,
            'preco': item.produto.preco,
            'subtotal': item.quantidade * item.produto.preco,
            'observacao': item.observacao or ""  # Para exibir no template
        }
        for item in itens_carrinho
    ]
    
    context = {
        'form': form,
        'itens': itens_resumo,
        'total': sum(item['subtotal'] for item in itens_resumo),
        'titulo': 'Confirmar Pedido',
    }
    
    return render(request, 'pedido/confirmar_pedido.html', context)







#--------------------------local entrega--------------------------------



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
            return redirect('carrinho')
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
