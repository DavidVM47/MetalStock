from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# CORS permite que el frontend (HTML) le hable al backend (Python) sin bloqueos de seguridad
CORS(app) 

def obtener_conexion():
    conn = sqlite3.connect('metalstock.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta para LEER el inventario
@app.route('/api/materiales', methods=['GET'])
def get_materiales():
    conexion = obtener_conexion()
    materiales = conexion.execute('SELECT * FROM materiales').fetchall()
    conexion.close()
    return jsonify([dict(ix) for ix in materiales])

# Ruta para AGREGAR un nuevo material
@app.route('/api/materiales', methods=['POST'])
def add_material():
    nuevo_material = request.get_json()
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO materiales (nombre, cantidad, unidad) VALUES (?, ?, ?)",
                   (nuevo_material['nombre'], nuevo_material['cantidad'], nuevo_material['unidad']))
    conexion.commit()
    conexion.close()
    return jsonify({'mensaje': 'Material agregado'}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)