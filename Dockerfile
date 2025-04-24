FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000


# Garante permissões para o SQLite
RUN mkdir -p /app/cardapio && \
    touch /app/cardapio/db.sqlite3 && \
    chmod 777 /app/cardapio/db.sqlite3
