from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import subprocess
import os

# 1. Importar la base de datos, los modelos y los enrutadores
from .database import engine
from . import models
from .routers import webhooks, dashboard

# 2. Crear las tablas en SQLite automáticamente si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Colmena Financiera")

# 3. Registrar las rutas en la aplicación
app.include_router(webhooks.router)
app.include_router(dashboard.router)

# 4. Resolución de ruta absoluta para la carpeta static (sin la 's')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_STATIC = os.path.join(BASE_DIR, "static")

# Montaje de archivos estáticos usando el nombre 'static'
app.mount("/static", StaticFiles(directory=RUTA_STATIC), name="static")

# 5. Endpoint para ejecutar tus scripts auxiliares desde la carpeta Programas
@app.post("/api/ejecutar-recordatorio")
def ejecutar_script_recordar():
    ruta_script = os.path.join(BASE_DIR, "Programas", "recordar.py")
    
    try:
        resultado = subprocess.run(
            ["python", ruta_script], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return {"status": "éxito", "salida": resultado.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "detalle": e.stderr}