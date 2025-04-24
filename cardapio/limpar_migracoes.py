import sqlite3

# Conectando ao banco de dados SQLite
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Deletando as migrações dos apps especificados
cursor.execute("DELETE FROM django_migrations WHERE app='produto'")
cursor.execute("DELETE FROM django_migrations WHERE app='pedido'")
cursor.execute("DELETE FROM django_migrations WHERE app='carrinho'")

# Comitando as mudanças e fechando a conexão
conn.commit()
conn.close()

print("Migrações limpas com sucesso!")
