import sqlite3

# Crea la base de datos y se conecta a ella
conexion = sqlite3.connect('metalstock.db')
cursor = conexion.cursor()

# Crea la tabla de materiales si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS materiales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cantidad REAL NOT NULL,
    unidad TEXT NOT NULL
)
''')

# Inserta un par de materiales de prueba
cursor.execute("INSERT INTO materiales (nombre, cantidad, unidad) VALUES ('Tubo rectangular 2x1', 50, 'Unidades')")
cursor.execute("INSERT INTO materiales (nombre, cantidad, unidad) VALUES ('Electrodos 6013', 10, 'Cajas')")

conexion.commit()
conexion.close()
print("¡Base de datos 'metalstock.db' inicializada correctamente!")