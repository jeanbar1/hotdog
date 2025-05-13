# impressao/views.py
from datetime import timezone
from django.http import JsonResponse
from serial import Serial
from .printers import PrinterService
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
@require_POST
def imprimir_pedido(request, pedido_id):
    from .models import Impressao
    
    impressao = Impressao.objects.get(pedido_id=pedido_id)
    result = PrinterService.send_print_job(impressao.conteudo)
    
    if result.get('success'):
        impressao.impresso = True
        impressao.data_impressao = timezone.now()
        impressao.save()
        return JsonResponse(result)
    else:
        impressao.tentativas += 1
        impressao.ultimo_erro = result.get('message', 'Erro desconhecido')
        impressao.save()
        return JsonResponse(result, status=400)
    
    
    

@csrf_exempt  # Permite requisições externas (apenas para teste)
def receber_webhook_impressao(request):
    if request.method == 'POST':
        try:
            conteudo = request.POST.get('content')
            
            # Conecta à impressora Bluetooth local
            printer = Serial(devfile='/dev/rfcomm0', baudrate=19200)
            printer.text(conteudo)
            printer.cut()
            
            return JsonResponse({"status": "success"})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    
    return JsonResponse({"status": "error", "message": "Método não permitido"})