import sqlite3
import pandas as pd

# 1. Crear conexión a la base de datos local
conn = sqlite3.connect('validacion_mvp.db')
cursor = conn.cursor()

# 2. Diseñar el esquema de la tabla de encuestas
cursor.execute('''
CREATE TABLE IF NOT EXISTS resultados_encuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfil TEXT,
    porcentaje_efectivo INTEGER,
    porcentaje_digital INTEGER,
    herramienta_actual TEXT,
    tiempo_dedicado TEXT,
    friccion_principal TEXT,
    disposicion_pagar_cop INTEGER,
    notas_adicionales TEXT
)
''')

# 3. Limpiar tabla si ya existe para evitar duplicados en pruebas
cursor.execute('DELETE FROM resultados_encuestas')

# 4. Insertar los datos extraídos de las entrevistas y encuestas
datos_encuestas = [
    # (perfil, % efectivo, % digital, herramienta, tiempo, friccion, WTP_COP, notas)
    ('Estudiante Universitario', 0, 100, 'Excel', '30 mins/mes', 'Ninguna aparente', 0, 'No pagaría'),
    ('Posgrado / Profesional', 0, 100, 'Excel / Nequi', 'Variable', 'Gasta rápido al transferir', 5000, 'Pagaría si clasifica categorías'),
    ('Estudiante', 60, 40, 'App banco', 'Ninguno', 'Pereza de anotar cada gasto', 0, 'Sugiere enfocar el modelo a empresas (B2B)'),
    ('Profesional / Ing', 0, 100, 'App banco', 'Poco', 'Revisar que todo cuadre', 0, 'Buena idea como adición a app bancaria, pero no pagaría'),
    ('Estudiante', 55, 45, 'Cuaderno', '1 hora/semana', 'Olvido de gastos', 10000, 'Pagaría un monto pequeño'),
    ('Profesional (María P)', 20, 80, 'App de gastos', 'Diario (abandonado)', 'Fricción manual diaria, olvido', 20000, 'Busca automatización de tarjetas'),
    ('Profesional (Niko)', 15, 85, 'Excel', '1 día/semana', 'Cansado de separar categorías a fin de mes', 50000, 'Pagaría por automatización total')
]

cursor.executemany('''
INSERT INTO resultados_encuestas (
    perfil, porcentaje_efectivo, porcentaje_digital, herramienta_actual, 
    tiempo_dedicado, friccion_principal, disposicion_pagar_cop, notas_adicionales
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', datos_encuestas)

conn.commit()

# 5. Consultar y mostrar los datos para análisis
df = pd.read_sql_query("SELECT * FROM resultados_encuestas", conn)
print(df.to_markdown(index=False))

conn.close()
