from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

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
        cursor.execute("SELECT ID FROM Admins WHERE Usuario=%s AND Contrasena=%s", (usuario, contrasena))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if admin:
            return jsonify({"success": True, "message": "Login exitoso"})
        else:
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
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
                SELECT s.ID, s.Nombre, s.Descripcion, s.URL_Imagen, s.Categoria_ID, c.Nombre as Categoria_Nombre 
                FROM Series s
                LEFT JOIN Categorias c ON s.Categoria_ID = c.ID
                WHERE s.Categoria_ID = %s
                ORDER BY s.ID DESC
            """, (categoria_id,))
        else:
            cursor.execute("""
                SELECT s.ID, s.Nombre, s.Descripcion, s.URL_Imagen, s.Categoria_ID, c.Nombre as Categoria_Nombre 
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
    categoria_id = data.get('categoria_id')
    
    if not nombre or not categoria_id:
        return jsonify({"success": False, "message": "Nombre y Categoría son requeridos"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Series (Nombre, Descripcion, URL_Imagen, Categoria_ID) VALUES (%s, %s, %s, %s)", 
                       (nombre, descripcion, url_imagen, categoria_id))
        conn.commit()
        cursor.close()
        conn.close()
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
    categoria_id = data.get('categoria_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Series SET Nombre=%s, Descripcion=%s, URL_Imagen=%s, Categoria_ID=%s WHERE ID=%s", 
                       (nombre, descripcion, url_imagen, categoria_id, id))
        conn.commit()
        cursor.close()
        conn.close()
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
        return jsonify({"success": True, "message": "Serie eliminada"})
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
        cursor.execute("INSERT INTO Imagenes_Productos (Nombre, URL_Imagen, Serie_ID, Categoria_ID, Precio) VALUES (%s, %s, %s, %s, %s)", 
                       (nombre, url_imagen, serie_id or None, categoria_id or None, precio))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Personaje añadido con éxito"})
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
        cursor.execute("UPDATE Imagenes_Productos SET Nombre=%s, URL_Imagen=%s, Serie_ID=%s, Categoria_ID=%s, Precio=%s WHERE ID=%s",
                       (nombre, url_imagen, serie_id or None, categoria_id or None, precio, id))
        conn.commit()
        cursor.close()
        conn.close()
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
        return jsonify({"success": True, "message": "Cuadro eliminado"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error BD: {str(e)}"}), 500

if __name__ == '__main__':
    print("Iniciando servidor de la API de Squirrel Frames en http://localhost:5000...")
    app.run(debug=True, port=5000)
