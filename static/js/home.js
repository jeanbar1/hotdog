// carrinho.js
document.addEventListener('DOMContentLoaded', function() {
    const quickAddModal = new bootstrap.Modal(document.getElementById('quickAddModal'));
    const quickAddForm = document.getElementById('quickAddForm');
    let currentProduct = null;

    // Configura botões de adição rápida
    document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
        btn.addEventListener('click', function() {
            currentProduct = {
                id: this.dataset.productId,
                name: this.dataset.productName,
                price: parseFloat(this.dataset.productPrice.replace(',', '.'))
            };

            // Atualiza o formulário
            document.getElementById('quickAddProductName').textContent = currentProduct.name;
            document.getElementById('quickAddPrice').textContent = `R$ ${currentProduct.price.toFixed(2).replace('.', ',')}`;
            document.querySelector('#quickAddModal .quantity-input').value = 1;
            document.getElementById('quickAddObservations').value = '';
            document.getElementById('quickAddTotal').textContent = `R$ ${currentProduct.price.toFixed(2).replace('.', ',')}`;
            
            // Atualiza action do formulário
            quickAddForm.action = `/carrinho/adicionar/${currentProduct.id}/`;
        });
    });

    // Configura controles de quantidade
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-input');
            let value = parseInt(input.value);
            
            if (this.classList.contains('minus-btn') && value > 1) {
                input.value = value - 1;
            } else if (this.classList.contains('plus-btn')) {
                input.value = value + 1;
            }
            
            updateTotalPrice();
        });
    });

    function updateTotalPrice() {
        if (currentProduct) {
            const quantity = parseInt(document.querySelector('#quickAddModal .quantity-input').value);
            const total = currentProduct.price * quantity;
            document.getElementById('quickAddTotal').textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
        }
    }
    // Configura botões de adição rápida
    function setupQuickAddButtons() {
        document.querySelectorAll('.quick-add-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                currentProduct = {
                    id: this.dataset.productId,
                    name: this.dataset.productName,
                    price: parseFloat(this.dataset.productPrice.replace(',', '.'))
                };

                // Atualiza o formulário
                document.getElementById('quickAddProductName').textContent = currentProduct.name;
                document.getElementById('quickAddPrice').textContent = `R$ ${formatCurrency(currentProduct.price)}`;
                document.querySelector('#quickAddModal .quantity-input').value = 1;
                document.getElementById('quickAddObservations').value = '';
                document.getElementById('quickAddTotal').textContent = `R$ ${formatCurrency(currentProduct.price)}`;
                
                // Atualiza action do formulário
                quickAddForm.action = `/carrinho/adicionar/${currentProduct.id}/`;
                
                quickAddModal.show();
            });
        });
    }

    // Configura envio do formulário
    function setupFormSubmit() {
        quickAddForm.addEventListener('submit', function(e) {
            // Validação básica
            const quantity = parseInt(document.querySelector('#quickAddModal .quantity-input').value);
            if (quantity < 1) {
                e.preventDefault();
                alert('A quantidade deve ser pelo menos 1');
                return;
            }
            
            // Fecha o modal após envio (o redirecionamento será tratado pelo servidor)
            quickAddModal.hide();
        });
    }

    // Inicialização
    function init() {
        setupQuantityControls();
        setupQuickAddButtons();
        setupFormSubmit();
    }

    init();
});