import requests
from io import BytesIO
from django.conf import settings
from escpos.printer import Dummy

class PrinterService:
    @staticmethod
    def send_print_job(content):
        """Envia o trabalho de impressão conforme o modo configurado"""
        if settings.PRINT_MODE == 'impressao':
            return {
                'success': False,
                'message': 'Use o link abaixo para imprimir via app',
                'deeplink': f"{settings.imprimir_pedido}{content}"
            }
        
        elif settings.PRINT_MODE == 'WEBHOOK':
            try:
                response = requests.post(
                    settings.PRINT_WEBHOOK_URL,
                    json={'content': content},
                    timeout=5
                )
                return response.json()
            except Exception as e:
                return {
                    'success': False,
                    'message': str(e)
                }
        
        else:  # TEST mode
            return {
                'success': True,
                'message': 'Modo teste - nada foi impresso'
            }

    @staticmethod
    def gerar_conteudo_impressao(pedido):
        """Gera o conteúdo formatado para impressão"""
        pointer = BytesIO()

        # Inicializa o objeto de impressão (Dummy é um exemplo, ajuste conforme sua necessidade)
        printer = Dummy()

        # Adiciona o título do pedido
        printer.text(f"Pedido # {pedido.id}\n")
        
        # Exemplo de como adicionar itens ao pedido
        for item in pedido.itens_pedido.all():
            printer.text(f"{item.produto.nome} - R${item.produto.preco_total} x {item.quantidade}\n")
        
        # Adiciona o total do pedido
        total = sum(item.produto.preco_total * item.quantidade for item in pedido.itens_pedido.all())
        printer.text(f"Total: R${total:.2f}\n")
        
        # Adiciona uma mensagem de agradecimento
        printer.text("Obrigado por comprar conosco!\n")
        
        # Cortar a página (se suportado pela impressora)
        printer.cut()
        
        # Acesso ao conteúdo de impressão (assumindo que 'output' seja um atributo de bytes)
        content = printer.output  # Acesso direto ao atributo
        
        # Remover qualquer caractere NUL (0x00) do conteúdo
        content = content.replace(b'\x00', b'')  # Remove caracteres NUL

        # Escreve no buffer
        pointer.write(content)

        # Volta o ponteiro para o início do buffer
        pointer.seek(0)
        
        # Retorna o conteúdo impresso como texto, usando a codificação latin1
        return pointer.getvalue().decode('latin1')
