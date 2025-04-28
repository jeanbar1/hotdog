document.addEventListener('DOMContentLoaded', function() {
    // Adiciona novo item ao formset
    document.getElementById('add-item').addEventListener('click', function() {
        const totalForms = document.getElementById('id_form-TOTAL_FORMS');
        const formIdx = parseInt(totalForms.value);
        const table = document.getElementById('itens-table').getElementsByTagName('tbody')[0];
        
        // Clone da última linha
        const newRow = table.rows[table.rows.length - 1].cloneNode(true);
        
        // Atualiza os IDs dos elementos
        newRow.querySelectorAll('input, select').forEach(function(el) {
            const name = el.name.replace(/-\d+-/, `-${formIdx}-`);
            const id = el.id.replace(/_\d+_/, `_${formIdx}_`);
            el.name = name;
            el.id = id;
            el.value = '';
        });
        
        // Reseta os valores de preço e subtotal
        newRow.querySelector('.preco-unitario').textContent = '-';
        newRow.querySelector('.subtotal').textContent = '-';
        
        // Mostra botão de remover se estiver oculto
        const removeBtn = newRow.querySelector('.remove-item');
        if (removeBtn) {
            removeBtn.style.display = 'block';
            removeBtn.addEventListener('click', function() {
                newRow.remove();
                atualizarTotalPedido();
            });
        }
        
        // Adiciona a nova linha
        table.appendChild(newRow);
        
        // Atualiza o contador de forms
        totalForms.value = formIdx + 1;
        
        // Adiciona eventos aos novos campos
        adicionarEventosLinha(newRow);
    });
    
    // Adiciona eventos a todas as linhas existentes
    document.querySelectorAll('.item-row').forEach(function(row) {
        adicionarEventosLinha(row);
        
        // Configura botão de remover se existir
        const removeBtn = row.querySelector('.remove-item');
        if (removeBtn) {
            removeBtn.style.display = 'block';
            removeBtn.addEventListener('click', function() {
                row.remove();
                atualizarTotalPedido();
            });
        }
    });
    
    // Função para adicionar eventos a uma linha
    function adicionarEventosLinha(row) {
        // Atualiza preços quando produto é selecionado
        const produtoSelect = row.querySelector('select[id$="-produto"]');
        if (produtoSelect) {
            produtoSelect.addEventListener('change', function() {
                const produtoId = this.value;
                
                if (produtoId) {
                    fetch(`/api/produtos/${produtoId}/preco/`)
                        .then(response => response.json())
                        .then(data => {
                            row.querySelector('.preco-unitario').textContent = 
                                `R$ ${data.preco.toFixed(2)}`;
                            calcularSubtotal(row);
                        })
                        .catch(() => {
                            row.querySelector('.preco-unitario').textContent = '-';
                            row.querySelector('.subtotal').textContent = '-';
                        });
                } else {
                    row.querySelector('.preco-unitario').textContent = '-';
                    row.querySelector('.subtotal').textContent = '-';
                }
                atualizarTotalPedido();
            });
        }
        
        // Recalcula subtotal quando quantidade muda
        const quantidadeInput = row.querySelector('input[id$="-quantidade"]');
        if (quantidadeInput) {
            quantidadeInput.addEventListener('change', function() {
                calcularSubtotal(row);
                atualizarTotalPedido();
            });
        }
    }
    
    // Calcula subtotal para uma linha
    function calcularSubtotal(row) {
        const quantidade = row.querySelector('input[id$="-quantidade"]').value;
        const precoText = row.querySelector('.preco-unitario').textContent;
        
        if (quantidade && precoText !== '-') {
            const preco = parseFloat(precoText.replace('R$ ', '').replace('.', '').replace(',', '.'));
            const subtotal = preco * parseInt(quantidade);
            row.querySelector('.subtotal').textContent = `R$ ${subtotal.toFixed(2).replace('.', ',')}`;
        } else {
            row.querySelector('.subtotal').textContent = '-';
        }
    }
    
    // Atualiza o total do pedido
    function atualizarTotalPedido() {
        let total = 0;
        
        document.querySelectorAll('.item-row').forEach(function(row) {
            const subtotalText = row.querySelector('.subtotal').textContent;
            
            if (subtotalText && subtotalText !== '-') {
                const subtotal = parseFloat(subtotalText.replace('R$ ', '').replace('.', '').replace(',', '.'));
                total += subtotal;
            }
        });
        
        document.getElementById('total-pedido').textContent = 
            `R$ ${total.toFixed(2).replace('.', ',')}`;
    }
    
    // Calcula totais iniciais
    atualizarTotalPedido();
});