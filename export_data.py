import json
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'squirrel_user',
    'password': 'squirrel123',
    'database': 'squirrel_db',
    'auth_plugin': 'mysql_native_password'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
except mysql.connector.Error:
    config = DB_CONFIG.copy()
    config.pop('auth_plugin', None)
    conn = mysql.connector.connect(**config)

cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT * FROM Categorias ORDER BY ID DESC")
categorias = cursor.fetchall()

cursor.execute("""
    SELECT s.ID, s.Nombre, s.Descripcion, s.URL_Imagen, s.Categoria_ID,
           c.Nombre as Categoria_Nombre
    FROM Series s
    LEFT JOIN Categorias c ON s.Categoria_ID = c.ID
    ORDER BY s.ID DESC
""")
series = cursor.fetchall()

cursor.execute("""
    SELECT p.ID, p.Nombre, p.URL_Imagen, p.Serie_ID, p.Categoria_ID, p.Precio,
           s.Nombre as Serie_Nombre, c.Nombre as Categoria_Nombre
    FROM Imagenes_Productos p
    LEFT JOIN Series s ON p.Serie_ID = s.ID
    LEFT JOIN Categorias c ON p.Categoria_ID = c.ID
    ORDER BY p.ID DESC
""")
productos = cursor.fetchall()

cursor.close()
conn.close()

data = {
    "categorias": categorias,
    "series": series,
    "productos": productos
}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("data.json generado correctamente")