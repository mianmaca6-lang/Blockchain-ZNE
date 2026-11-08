import sqlite3

def setup_admin_db():
    conn = sqlite3.connect('colmena_finanzas_mvp.db')
    cursor = conn.cursor()

    # (Aquí irían las tablas de usuarios y transacciones que vimos antes)
    # ...

    # 1. Tabla para rastrear la actividad y el bombillito verde
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sesiones_activas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        token_sesion TEXT,
        ip TEXT,
        ultimo_visto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')

    # 2. Tabla para rastrear clics y comportamiento (Analíticas)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registro_eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        tipo_evento TEXT, -- Ej: 'page_view', 'click_btn_ahorro', 'ingreso_fallido'
        detalles TEXT, -- JSON o texto extra si es necesario
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')

    conn.commit()
    conn.close()
