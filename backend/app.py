from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import bcrypt
import json
import requests
import base64
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'squirrel_user',
    'password': 'squirrel123',
    'database': 'squirrel_db',
    'auth_plugin': 'mysql_native_password' 
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        fallback_config = DB_CONFIG.copy()
        fallback_config.pop('auth_plugin', None)
        return mysql.connector.connect(**fallback_config)

def exportar_data_json():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Categorias ORDER BY ID DESC")
        categorias = cursor.fetchall()
        cursor.execute("""
            SELECT s.ID, s.Nombre, s.Descripcion, s.URL_Imagen, s.Precio, s.Categoria_ID,
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
        data = {"categorias": categorias, "series": series, "productos": productos}
        ruta = os.path.join(BASE_DIR, 'data.json')
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, "data.json exportado correctamente"
    except Exception as e:
        return False, str(e)

# ==========================================
# RUTAS API: AUTENTICACIÓN
# ==========================================
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    data = request.json
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ID, Contrasena FROM Admins WHERE Usuario=%s", (usuario,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if admin and bcrypt.checkpw(contrasena.encode('utf-8'), admin['Contrasena'].encode('utf-8')):
            return jsonify({"success": True, "message": "Login exitoso"})
        else:
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    
    if not usuario or not contrasena:
        return jsonify({"success": False, "message": "Usuario y contraseña requeridos"}), 400
    
    try:
        hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Admins (Usuario, Contrasena) VALUES (%s, %s)", (usuario, hashed.decode('utf-8')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Admin registrado con éxito"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

# ==========================================
# RUTAS API: CATEGORÍAS (NIVEL 1)
# ==========================================
@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Categorias ORDER BY ID DESC")
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/categorias', methods=['POST'])
def add_categoria():
    data = request.json
    nombre = data.get('nombre')
    url_imagen = data.get('url_imagen', '')
    if not nombre:
        return jsonify({"success": False, "message": "El nombre es requerido"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Categorias (Nombre, URL_Imagen) VALUES (%s, %s)", (nombre, url_imagen))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Categoría añadida con éxito"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/categorias/<int:id>', methods=['PUT', 'OPTIONS'])
def update_categoria(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    nombre = data.get('nombre')
    url_imagen = data.get('url_imagen', '')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Categorias SET Nombre=%s, URL_Imagen=%s WHERE ID=%s", (nombre, url_imagen, id))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Categoría actualizada"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/categorias/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_categoria(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Categorias WHERE ID=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Categoría eliminada"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500


# ==========================================
# RUTAS API: SERIES/COLECCIONES (NIVEL 2)
# ==========================================
@app.route('/api/series', methods=['GET'])
def get_series():
    categoria_id = request.args.get('categoria_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if categoria_id:
            cursor.execute("""
                SELECT s.ID, s.Nombre, s.Descripcion, s.URL_Imagen, s.Precio, s.Categoria_ID, c.Nombre as Categoria_Nombre 
                FROM Series s
                LEFT JOIN Categorias c ON s.Categoria_ID = c.ID
                WHERE s.Categoria_ID = %s
                ORDER BY s.ID DESC
            """, (categoria_id,))
        else:
            cursor.execute("""
                SELECT s.ID, s.Nombre, s.Descripcion, s.URL_Imagen, s.Precio, s.Categoria_ID, c.Nombre as Categoria_Nombre 
                FROM Series s
                LEFT JOIN Categorias c ON s.Categoria_ID = c.ID
                ORDER BY s.ID DESC
            """)
        series = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(series)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/series', methods=['POST'])
def add_serie():
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')
    url_imagen = data.get('url_imagen', '')
    precio = data.get('precio', '')
    categoria_id = data.get('categoria_id')
    
    if not nombre or not categoria_id:
        return jsonify({"success": False, "message": "Nombre y Categoría son requeridos"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Series (Nombre, Descripcion, URL_Imagen, Precio, Categoria_ID) VALUES (%s, %s, %s, %s, %s)", 
                       (nombre, descripcion, url_imagen, precio, categoria_id))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Serie añadida con éxito"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/series/<int:id>', methods=['PUT', 'OPTIONS'])
def update_serie(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')
    url_imagen = data.get('url_imagen', '')
    precio = data.get('precio', '')
    categoria_id = data.get('categoria_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Series SET Nombre=%s, Descripcion=%s, URL_Imagen=%s, Precio=%s, Categoria_ID=%s WHERE ID=%s", 
                       (nombre, descripcion, url_imagen, precio, categoria_id, id))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Serie actualizada"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/series/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_serie(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Series WHERE ID=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Serie eliminada"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/series/<int:id>/sincronizar-precios', methods=['POST', 'OPTIONS'])
def sync_series_prices(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Precio FROM Series WHERE ID=%s", (id,))
        serie = cursor.fetchone()
        if not serie or not serie['Precio']:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "La colección no tiene precio definido"}), 400
        cursor.execute("UPDATE Imagenes_Productos SET Precio=%s WHERE Serie_ID=%s", (serie['Precio'], id))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": f"Precio '{serie['Precio']}' aplicado a todos los productos"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500


# ==========================================
# RUTAS API: PRODUCTOS / PERSONAJES (NIVEL 3)
# ==========================================
@app.route('/api/productos', methods=['GET'])
def get_productos():
    serie_id = request.args.get('serie_id')
    categoria_id = request.args.get('categoria_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT p.ID, p.Nombre, p.URL_Imagen, p.Serie_ID, p.Categoria_ID, p.Precio,
                   s.Nombre as Serie_Nombre, c.Nombre as Categoria_Nombre
            FROM Imagenes_Productos p
            LEFT JOIN Series s ON p.Serie_ID = s.ID
            LEFT JOIN Categorias c ON p.Categoria_ID = c.ID
            WHERE 1=1
        """
        params = []
        if serie_id:
            query += " AND p.Serie_ID = %s"
            params.append(serie_id)
        if categoria_id:
            query += " AND p.Categoria_ID = %s"
            params.append(categoria_id)
        query += " ORDER BY p.ID DESC"
        cursor.execute(query, params)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/productos', methods=['POST'])
def add_producto():
    data = request.json
    nombre = data.get('nombre')
    url_imagen = data.get('url_imagen')
    serie_id = data.get('serie_id')
    categoria_id = data.get('categoria_id')
    precio = data.get('precio', '')
    
    if not nombre or not url_imagen:
        return jsonify({"success": False, "message": "Nombre e imagen son requeridos"}), 400
    if not serie_id and not categoria_id:
        return jsonify({"success": False, "message": "Debe pertenecer a una colección o categoría"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if not serie_id:
            cursor2 = conn.cursor(dictionary=True)
            cursor2.execute("SELECT ID FROM Series WHERE Nombre='Sin Coleccion' AND (Categoria_ID IS NULL OR Categoria_ID = 0)")
            row = cursor2.fetchone()
            if row:
                serie_id = row['ID']
            cursor2.close()

        cursor.execute("INSERT INTO Imagenes_Productos (Nombre, URL_Imagen, Serie_ID, Categoria_ID, Precio) VALUES (%s, %s, %s, %s, %s)", 
                       (nombre, url_imagen, serie_id or None, categoria_id or None, precio))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Personaje anadido con exito"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/productos/<int:id>', methods=['PUT', 'OPTIONS'])
def update_producto(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    nombre = data.get('nombre')
    url_imagen = data.get('url_imagen')
    serie_id = data.get('serie_id')
    categoria_id = data.get('categoria_id')
    precio = data.get('precio', '')
    if not nombre or not url_imagen:
        return jsonify({"success": False, "message": "Nombre e imagen son requeridos"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if not serie_id:
            cursor2 = conn.cursor(dictionary=True)
            cursor2.execute("SELECT ID FROM Series WHERE Nombre='Sin Coleccion' AND (Categoria_ID IS NULL OR Categoria_ID = 0)")
            row = cursor2.fetchone()
            if row:
                serie_id = row['ID']
            cursor2.close()

        cursor.execute("UPDATE Imagenes_Productos SET Nombre=%s, URL_Imagen=%s, Serie_ID=%s, Categoria_ID=%s, Precio=%s WHERE ID=%s",
                       (nombre, url_imagen, serie_id or None, categoria_id or None, precio, id))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Personaje actualizado"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_producto(id):
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Imagenes_Productos WHERE ID=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        exportar_data_json()
        return jsonify({"success": True, "message": "Cuadro eliminado"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

@app.route('/api/exportar', methods=['POST', 'GET'])
def exportar():
    success, msg = exportar_data_json()
    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "message": msg}), 500

@app.route('/api/subir-imagen', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({"success": False, "message": "No se envió imagen"}), 400
    
    file = request.files['imagen']
    if not file.filename:
        return jsonify({"success": False, "message": "Archivo vacío"}), 400
    
    try:
        img_data = base64.b64encode(file.read()).decode()
        r = requests.post('https://api.imgbb.com/1/upload', data={
            'key': '3282f80fe946fadc664bbd4631560d23',
            'image': img_data
        })
        data = r.json()
        if data.get('success'):
            return jsonify({"success": True, "url": data['data']['url']})
        return jsonify({"success": False, "message": "Error al subir a ImgBB"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def servir_paginas(path):
    if not path:
        return send_from_directory(BASE_DIR, 'index.html')
    try:
        return send_from_directory(BASE_DIR, path)
    except Exception:
        return send_from_directory(BASE_DIR, 'index.html')

def seed_default_admin():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("REPLACE INTO Admins (Usuario, Contrasena) VALUES (%s, %s)", ('admin', hashed.decode('utf-8')))
        conn.commit()
        print("[OK] Admin por defecto actualizado: usuario='admin', contrasena='admin123'")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] No se pudo crear admin por defecto: {e}")

def seed_sin_coleccion():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Encontrar series "Sin Coleccion" con categoria (las creadas antes)
        cursor.execute("SELECT ID FROM Series WHERE Nombre='Sin Coleccion' AND Categoria_ID IS NOT NULL AND Categoria_ID != 0")
        cat_entries = [row['ID'] for row in cursor.fetchall()]

        # Crear o encontrar el unico "Sin Coleccion" (sin categoria)
        cursor.execute("SELECT ID FROM Series WHERE Nombre='Sin Coleccion' AND (Categoria_ID IS NULL OR Categoria_ID = 0)")
        master = cursor.fetchone()
        if master:
            master_id = master['ID']
        else:
            cursor.execute("INSERT INTO Series (Nombre, Descripcion) VALUES ('Sin Coleccion', 'Productos sin coleccion asignada')")
            conn.commit()
            master_id = cursor.lastrowid
            print("[OK] Serie 'Sin Coleccion' creada")

        # Migrar productos desde las entradas por categoria al unico
        if cat_entries:
            placeholders = ','.join(['%s'] * len(cat_entries))
            cursor.execute(f"UPDATE Imagenes_Productos SET Serie_ID=%s WHERE Serie_ID IN ({placeholders})",
                           (master_id, *cat_entries))
            if cursor.rowcount > 0:
                conn.commit()
                print(f"[OK] {cursor.rowcount} producto(s) migrado(s) a unico 'Sin Coleccion'")
            cursor.execute(f"DELETE FROM Series WHERE ID IN ({placeholders})", cat_entries)
            conn.commit()
            print(f"[OK] {len(cat_entries)} entrada(s) 'Sin Coleccion' por categoria eliminada(s)")

        # Migrar productos con Serie_ID = NULL
        cursor.execute("SELECT COUNT(*) as cnt FROM Imagenes_Productos WHERE Serie_ID IS NULL")
        count = cursor.fetchone()['cnt']
        if count > 0:
            cursor.execute("UPDATE Imagenes_Productos SET Serie_ID=%s WHERE Serie_ID IS NULL", (master_id,))
            conn.commit()
            print(f"[OK] {count} producto(s) sin coleccion migrado(s) a 'Sin Coleccion'")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] No se pudo crear serie 'Sin Coleccion': {e}")

if __name__ == '__main__':
    seed_default_admin()
    seed_sin_coleccion()
    print("Iniciando servidor de Poster&Poster en http://localhost:5000...")
    app.run(port=5000)
