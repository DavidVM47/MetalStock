from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def db_conexion():
    conn = sqlite3.connect('metalstock.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/materiales', methods=['GET', 'POST'])
def gestionar_materiales():
    conn = db_conexion()
    if request.method == 'GET':
        items = conn.execute('SELECT * FROM materiales').fetchall()
        return jsonify([dict(i) for i in items])
    nuevo = request.get_json()
    conn.execute('INSERT INTO materiales (nombre, cantidad, unidad) VALUES (?, ?, ?)',
                 (nuevo['nombre'], nuevo['cantidad'], nuevo['unidad']))
    conn.commit()
    return jsonify({'msj': 'ok'})

@app.route('/api/clientes', methods=['GET', 'POST'])
def gestionar_clientes():
    conn = db_conexion()
    if request.method == 'GET':
        items = conn.execute('SELECT * FROM clientes').fetchall()
        return jsonify([dict(i) for i in items])
    nuevo = request.get_json()
    conn.execute('INSERT INTO clientes (nombre, trabajo) VALUES (?, ?)',
                 (nuevo['nombre'], nuevo['trabajo']))
    conn.commit()
    return jsonify({'msj': 'ok'})

@app.route('/api/vincular', methods=['POST'])
def vincular_material():
    datos = request.get_json()
    conn = db_conexion()
    mat = conn.execute('SELECT nombre FROM materiales WHERE id = ?', (datos['material_id'],)).fetchone()
    # Restar del stock
    conn.execute('UPDATE materiales SET cantidad = cantidad - ? WHERE id = ?',
                 (datos['cantidad'], datos['material_id']))
    # Guardar en consumo
    conn.execute('INSERT INTO consumo_proyectos (cliente_id, material_id, material_nombre, cantidad_gastada) VALUES (?, ?, ?, ?)',
                 (datos['cliente_id'], datos['material_id'], mat['nombre'], datos['cantidad']))
    conn.commit()
    return jsonify({'msj': 'ok'})

@app.route('/api/desvincular', methods=['POST'])
def desvincular_material():
    datos = request.get_json() # Recibe consumo_id
    conn = db_conexion()
    # 1. Obtener datos del consumo antes de borrarlo
    consumo = conn.execute('SELECT * FROM consumo_proyectos WHERE id = ?', (datos['consumo_id'],)).fetchone()
    if consumo:
        # 2. Devolver la cantidad al inventario original
        conn.execute('UPDATE materiales SET cantidad = cantidad + ? WHERE id = ?',
                     (consumo['cantidad_gastada'], consumo['material_id']))
        # 3. Borrar el registro de consumo
        conn.execute('DELETE FROM consumo_proyectos WHERE id = ?', (datos['consumo_id'],))
        conn.commit()
    return jsonify({'msj': 'Material devuelto al stock'})

@app.route('/api/reporte/<int:cliente_id>', methods=['GET'])
def ver_reporte(cliente_id):
    conn = db_conexion()
    reporte = conn.execute('SELECT * FROM consumo_proyectos WHERE cliente_id = ?', (cliente_id,)).fetchall()
    return jsonify([dict(r) for r in reporte])

if __name__ == '__main__':
    app.run(debug=True, port=5000)