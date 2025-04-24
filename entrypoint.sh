#!/bin/sh

echo "Rodando migrações..."
python cardapio/manage.py migrate

echo "Coletando arquivos estáticos..."
python cardapio/manage.py collectstatic --no-input --clear

exec "$@"
