from produto.models import CategoriaProduto

def variaveis_globais(request):
    var = {
        'nome_site': 'HotDogChapaQuente',
        'categorias': CategoriaProduto.objects.all(),
    }
    
    return var