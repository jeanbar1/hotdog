#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Configuração específica para Render
if [[ $RENDER ]]; then
  echo "Configurando para ambiente Render..."
  # Nada específico necessário para Bluetooth
fi