document.addEventListener('DOMContentLoaded', () => {
    // Função para atualizar todos os contadores do carrinho na página
    function updateCartCounters() {
      const totalCount = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
      
      // Atualiza o contador no ícone do carrinho (se existir)
      if (document.getElementById('cart-count')) {
        document.getElementById('cart-count').textContent = totalCount;
      }
      
      // Atualiza o contador na navbar (se existir)
      const navCounters = document.querySelectorAll('.cart-counter');
      navCounters.forEach(counter => {
        counter.textContent = totalCount;
      });
      
      localStorage.setItem('cart', JSON.stringify(cart));
    }

    // Carrega o carrinho do localStorage
    let cart = JSON.parse(localStorage.getItem('cart')) || {};
    
    // Atualiza os contadores ao carregar a página
    updateCartCounters();

    // Evento para adicionar itens ao carrinho (se houver botões de adicionar)
    document.querySelectorAll('.add-to-cart').forEach(button => {
      button.addEventListener('click', () => {
        const itemCard = button.closest('.menu-item');
        const id = itemCard.dataset.id;
        cart[id] = (cart[id] || 0) + 1;
        updateCartCounters();
        
        // Feedback visual
        button.textContent = '✔ Adicionado';
        setTimeout(() => button.textContent = 'Adicionar', 1000);
      });
    });

    // Se você precisar sincronizar com o servidor periodicamente
    function syncCartWithServer() {
      // Implemente aqui a lógica para sincronizar com o backend
      // Pode ser uma chamada AJAX para atualizar o carrinho no servidor
    }
    
    // Sincroniza a cada 30 segundos (opcional)
    setInterval(syncCartWithServer, 30000);
  });