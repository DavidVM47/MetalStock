from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def db_conexion():
    conn = sqlite3.connect('metalstock.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- RUTA PARA LOS BOTONES + Y - ---
@app.route('/api/materiales/ajuste', methods=['POST'])
def ajustar_stock():
    try:
        datos = request.get_json()
        m_id = datos.get('material_id')
        cambio = datos.get('cambio') # Recibe 1 o -1
        
        conn = db_conexion()
        conn.execute('UPDATE materiales SET cantidad = cantidad + ? WHERE id = ?', (cambio, m_id))
        conn.commit()
        conn.close()
        return jsonify({'msj': 'Stock actualizado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- OTRAS RUTAS (Materiales, Clientes, Vincular) ---
@app.route('/api/materiales', methods=['GET', 'POST'])
def gestionar_materiales():
    conn = db_conexion()
    if request.method == 'GET':
        items = conn.execute('SELECT * FROM materiales').fetchall()
        conn.close()
        return jsonify([dict(i) for i in items])
    
    nuevo = request.get_json()
    conn.execute('INSERT INTO materiales (nombre, cantidad, unidad) VALUES (?, ?, ?)',
                 (nuevo['nombre'], nuevo['cantidad'], nuevo['unidad']))
    conn.commit()
    conn.close()
    return jsonify({'msj': 'ok'})

@app.route('/api/clientes', methods=['GET', 'POST'])
def gestionar_clientes():
    conn = db_conexion()
    if request.method == 'GET':
        items = conn.execute('SELECT * FROM clientes').fetchall()
        conn.close()
        return jsonify([dict(i) for i in items])
    nuevo = request.get_json()
    conn.execute('INSERT INTO clientes (nombre, trabajo) VALUES (?, ?)',
                 (nuevo['nombre'], nuevo['trabajo']))
    conn.commit()
    conn.close()
    return jsonify({'msj': 'ok'})

@app.route('/api/vincular', methods=['POST'])
def vincular_material():
    datos = request.get_json()
    conn = db_conexion()
    mat = conn.execute('SELECT * FROM materiales WHERE id = ?', (datos['material_id'],)).fetchone()
    
    if mat['cantidad'] < float(datos['cantidad']):
        conn.close()
        return jsonify({'error': 'Stock insuficiente'}), 400

    conn.execute('UPDATE materiales SET cantidad = cantidad - ? WHERE id = ?',
                 (datos['cantidad'], datos['material_id']))
    conn.execute('INSERT INTO consumo_proyectos (cliente_id, material_id, material_nombre, cantidad_gastada) VALUES (?, ?, ?, ?)',
                 (datos['cliente_id'], datos['material_id'], mat['nombre'], datos['cantidad']))
    conn.commit()
    conn.close()
    return jsonify({'msj': 'ok'})

@app.route('/api/historial_global', methods=['GET'])
def historial_global():
    conn = db_conexion()
    movimientos = conn.execute('''
        SELECT c.nombre as cliente, cp.material_nombre, cp.cantidad_gastada 
        FROM consumo_proyectos cp 
        JOIN clientes c ON cp.cliente_id = c.id 
        ORDER BY cp.id DESC LIMIT 5
    ''').fetchall()
    conn.close()
    return jsonify([dict(m) for m in movimientos])

@app.route('/api/reporte/<int:cliente_id>', methods=['GET'])
def ver_reporte(cliente_id):
    conn = db_conexion()
    reporte = conn.execute('SELECT * FROM consumo_proyectos WHERE cliente_id = ?', (cliente_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in reporte])

@app.route('/api/desvincular', methods=['POST'])
def desvincular():
    datos = request.get_json()
    conn = db_conexion()
    consumo = conn.execute('SELECT * FROM consumo_proyectos WHERE id = ?', (datos['consumo_id'],)).fetchone()
    if consumo:
        conn.execute('UPDATE materiales SET cantidad = cantidad + ? WHERE id = ?',
                     (consumo['cantidad_gastada'], consumo['material_id']))
        conn.execute('DELETE FROM consumo_proyectos WHERE id = ?', (datos['consumo_id'],))
        conn.commit()
    conn.close()
    return jsonify({'msj': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)