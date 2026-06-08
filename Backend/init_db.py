import psycopg2

def inicializar_base_de_datos():
    try:
        # Conexión orientada a la nueva base de datos para Python
        conn = psycopg2.connect(
            host="localhost",
            database="metalstock_python", # <--- Base de datos independiente
            user="postgres",
            password="admin",      # <--- COLOCA AQUÍ TU CONTRASEÑA DE POSTGRES
            port="5432"
        )
        cursor = conn.cursor()

        print("Creando tablas en PostgreSQL (Base de datos: metalstock_python)...")

        # 1. Tabla de Materiales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materiales (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                cantidad REAL NOT NULL DEFAULT 0.0,
                unidad VARCHAR(50) NOT NULL
            )
        ''')

        # 2. Tabla de Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                trabajo VARCHAR(255) NOT NULL
            )
        ''')

        # 3. Tabla de Historial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumo_proyectos (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER,
                material_id INTEGER,
                material_nombre VARCHAR(255) NOT NULL,
                cantidad_gastada REAL NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
                FOREIGN KEY (material_id) REFERENCES materiales (id) ON DELETE SET NULL
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("¡Base de datos en PostgreSQL inicializada con éxito!")

    except Exception as e:
        print(f"Error al conectar o inicializar PostgreSQL: {e}")

if __name__ == '__main__':
    inicializar_base_de_datos()