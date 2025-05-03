document.addEventListener('DOMContentLoaded', () => {
  // Elementos
  const categoryButtons = document.querySelectorAll('.menu-category-button');
  const searchInput = document.getElementById('search-input');
  const menuItems = document.querySelectorAll('.menu-item');
  const cartCountElem = document.getElementById('cart-count');

  // Estado do carrinho (carrega de localStorage ou inicia vazio)
  let cart = JSON.parse(localStorage.getItem('cart')) || {};

  // Atualiza o contador de itens no carrinho
  function updateCartCount() {
    const totalCount = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
    cartCountElem.textContent = totalCount;
    localStorage.setItem('cart', JSON.stringify(cart));
  }

  // Filtra itens pela categoria
  categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const cat = btn.dataset.category;
      menuItems.forEach(item => {
        if (cat === 'all' || item.dataset.categories.includes(cat)) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  // Busca em tempo real pelo nome ou descrição
  searchInput.addEventListener('input', () => {
    const term = searchInput.value.trim().toLowerCase();
    menuItems.forEach(item => {
      const name = item.querySelector('.item-name').textContent.toLowerCase();
      const desc = item.querySelector('.item-description').textContent.toLowerCase();
      if (name.includes(term) || desc.includes(term)) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  });

  // Hook em todos os botões “Adicionar ao carrinho”
  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.dataset.id;

      // Incrementa quantidade no carrinho
      cart[id] = (cart[id] || 0) + 1;
      updateCartCount();

      // Feedback visual
      button.textContent = '✔ Adicionado';
      button.disabled = true;
      setTimeout(() => {
        button.innerHTML = '<i class="fas fa-cart-plus me-1"></i> Adicionar';
        button.disabled = false;
      }, 1000);
    });
  });

  // Inicializa contador na carga da página
  updateCartCount();
});

// Preview de imagem para input file
document.getElementById('id_imagem')?.addEventListener('change', function(e) {
  if (e.target.files.length) {
    const preview = document.getElementById('image-preview');
    preview.src = URL.createObjectURL(e.target.files[0]);
    preview.style.display = 'block';
  }
});
