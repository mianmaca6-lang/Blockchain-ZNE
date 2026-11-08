from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

import os # <-- NUEVO

from ..database import SessionLocal
from ..models import RegistroArchivo, ReglaClasificacion, Cliente



router = APIRouter(tags=["Vistas HTML"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUTA_TEMPLATES = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=RUTA_TEMPLATES)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def panel_principal(request: Request, db: Session = Depends(get_db)):
    # 1. Consultar métricas rápidas
    total_archivos = db.query(RegistroArchivo).count()
    archivos_pendientes = db.query(RegistroArchivo).filter(RegistroArchivo.estado == "input").count()
    archivos_clasificados = db.query(RegistroArchivo).filter(RegistroArchivo.estado == "check").count()
    total_reglas = db.query(ReglaClasificacion).count()

    # 2. Obtener los últimos 5 archivos procesados para la tabla
    ultimos_archivos = db.query(RegistroArchivo).order_by(RegistroArchivo.id.desc()).limit(5).all()

   
   # Envía todo a Jinja2 (CORREGIDO: 'request' va de primero)
    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "total_archivos": total_archivos,
        "pendientes": archivos_pendientes,
        "clasificados": archivos_clasificados,
        "total_reglas": total_reglas,
        "ultimos_archivos": ultimos_archivos
    })