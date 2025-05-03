document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const imageInput = document.getElementById('id_imagem');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');
    const defaultImageSrc = "{% static 'img/user-2935527__340.png' %}";
    const form = document.getElementById('registration-form');
    const submitBtn = document.getElementById('submit-btn');

    // Preview da imagem
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];

                // Verifica o tamanho do arquivo (max 2MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('A imagem não pode ser maior que 2MB');
                    this.value = '';
                    return;
                }

                // Verifica o tipo do arquivo
                const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    removeImageBtn.style.display = 'inline-block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Remover imagem selecionada
    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', function() {
            imageInput.value = '';
            imagePreview.src = defaultImageSrc;
            this.style.display = 'none';
        });
    }

    // Toggle para mostrar/esconder senha
    function togglePassword(button, inputId) {
        const input = document.getElementById(inputId);
        const icon = button.querySelector('img');

        if (input.type === 'password') {
            input.type = 'text';
            icon.src = "/static/img/hide-password.png";
            icon.alt = "Ocultar senha";
        } else {
            input.type = 'password';
            icon.src = "/static/img/show-password.png";
            icon.alt = "Mostrar senha";
        }
    }

    // Adiciona evento aos botões de toggle
    const toggleButtons = document.querySelectorAll('[onclick^="togglePassword"]');
    toggleButtons.forEach(button => {
        const inputId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        button.addEventListener('click', function() {
            togglePassword(this, inputId);
        });
    });

    // Feedback durante o envio do formulário
    if (form) {
        form.addEventListener('submit', function() {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cadastrando...';
        });
    }

    // Inicializa tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Máscara para telefone
    const telefoneInput = document.getElementById('id_telefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.substring(0, 11);

            if (value.length > 2) {
                value = `(${value.substring(0, 2)}) ${value.substring(2)}`;
            }
            if (value.length > 10) {
                value = `${value.substring(0, 10)}-${value.substring(10)}`;
            }
            e.target.value = value;
        });
    }
});
