from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import DictCursor
import os

# Localizamos automáticamente tu carpeta Frontend
ruta_frontend = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Frontend'))

app = Flask(__name__, static_folder=ruta_frontend, static_url_path='')
CORS(app)

def db_conexion():
    # Conexión centralizada a la base de datos de Python
    conn = psycopg2.connect(
        host="localhost",
        database="metalstock_python", # <--- Conectado a la BD independiente
        user="postgres",
        password="admin",      # <--- COLOCA AQUÍ TU CONTRASEÑA DE POSTGRES
        port="5432"
    )
    return conn

@app.route('/')
def index():
    return app.send_static_file('index.html')

# ==========================================
# MATERIALES (BODEGA)
# ==========================================
@app.route('/api/materiales', methods=['GET', 'POST'])
def gestionar_materiales():
    conn = db_conexion()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM materiales')
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([dict(i) for i in items])
    
    nuevo = request.get_json()
    cursor.execute('INSERT INTO materiales (nombre, cantidad, unidad) VALUES (%s, %s, %s)',
                 (nuevo['nombre'], nuevo['cantidad'], nuevo['unidad']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'ok'})

@app.route('/api/materiales/<int:id>', methods=['DELETE'])
def borrar_material(id):
    conn = db_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM materiales WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'Material eliminado'})

@app.route('/api/materiales/<int:id>/stock', methods=['PUT'])
def ajustar_stock(id):
    ajuste = float(request.args.get('ajuste', 0))
    
    conn = db_conexion()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute('SELECT cantidad FROM materiales WHERE id = %s', (id,))
    mat = cursor.fetchone()
    
    if mat:
        nuevo_stock = float(mat['cantidad']) + ajuste
        if nuevo_stock < 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'El stock no puede ser negativo'}), 400
            
        cursor.execute('UPDATE materiales SET cantidad = %s WHERE id = %s', (nuevo_stock, id))
        conn.commit()
    
    cursor.close()
    conn.close()
    return jsonify({'msj': 'Stock actualizado'})

# ==========================================
# CLIENTES
# ==========================================
@app.route('/api/clientes', methods=['GET', 'POST'])
def gestionar_clientes():
    conn = db_conexion()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM clientes')
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([dict(i) for i in items])
        
    nuevo = request.get_json()
    cursor.execute('INSERT INTO clientes (nombre, trabajo) VALUES (%s, %s)',
                 (nuevo['nombre'], nuevo['trabajo']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'ok'})

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def borrar_cliente(id):
    conn = db_conexion()
    cursor = conn.cursor()
    # Borrado manual de consumos relacionados por seguridad
    cursor.execute('DELETE FROM consumo_proyectos WHERE cliente_id = %s', (id,))
    cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'Cliente y su historial borrados'})

# ==========================================
# CONSUMO E HISTORIAL
# ==========================================
@app.route('/api/consumos/registrar', methods=['POST'])
def registrar_consumo():
    cliente_id = request.args.get('clienteId')
    material_id = request.args.get('materialId')
    cantidad = float(request.args.get('cantidadUsada', 0))
    
    conn = db_conexion()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    cursor.execute('SELECT * FROM materiales WHERE id = %s', (material_id,))
    mat = cursor.fetchone()
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
    cli = cursor.fetchone()
    
    if not mat or not cli:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Cliente o Material no encontrado'}), 404

    if float(mat['cantidad']) < cantidad:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Stock insuficiente'}), 400

    cursor.execute('UPDATE materiales SET cantidad = cantidad - %s WHERE id = %s', (cantidad, material_id))
    cursor.execute('''INSERT INTO consumo_proyectos 
                    (cliente_id, material_id, material_nombre, cantidad_gastada) 
                    VALUES (%s, %s, %s, %s)''', 
                 (cliente_id, material_id, mat['nombre'], cantidad))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'Consumo registrado'})

@app.route('/api/consumos', methods=['GET'])
def listar_historial():
    conn = db_conexion()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute('''
        SELECT cp.id, cp.cantidad_gastada, c.nombre as cliente_nombre, m.nombre as material_nombre
        FROM consumo_proyectos cp
        LEFT JOIN clientes c ON cp.cliente_id = c.id
        LEFT JOIN materiales m ON cp.material_id = m.id
        ORDER BY cp.id DESC
    ''')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    resultados = []
    for f in filas:
        resultados.append({
            "id": f["id"],
            "cliente": {"nombre": f["cliente_nombre"]} if f["cliente_nombre"] else None,
            "material": {"nombre": f["material_nombre"]} if f["material_nombre"] else None,
            "cantidadUsada": float(f["cantidad_gastada"])
        })
    return jsonify(resultados)

@app.route('/api/consumos/<int:id>', methods=['DELETE'])
def borrar_registro_historial(id):
    conn = db_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM consumo_proyectos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'Registro eliminado'})

@app.route('/api/consumos/vaciar', methods=['DELETE'])
def vaciar_historial():
    conn = db_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM consumo_proyectos')
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'msj': 'Historial vaciado por completo'})

if __name__ == '__main__':
    app.run(debug=True, port=8080)