from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

# Importaciones relativas según la estructura del proyecto
from ..database import SessionLocal
from ..models import RegistroArchivo, ReglaClasificacion

router = APIRouter(prefix="/api/webhooks", tags=["Ingesta n8n"])

# Dependencia para inyectar la sesión de la base de datos de forma segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Esquema estricto: Lo que el nodo HTTP Request de n8n DEBE enviar
class N8nPayload(BaseModel):
    cliente_id: int
    nombre_archivo: str
    texto_extraido: str
    monto_total: Optional[float] = 0.0
    url_origen: Optional[str] = None

@router.post("/ingesta-factura")
def recibir_datos_n8n(
    payload: N8nPayload, 
    db: Session = Depends(get_db), 
    x_api_token: str = Header(None)
):
    # Seguridad básica para evitar inyecciones de terceros
    if x_api_token != "TU_TOKEN_SECRETO_COLMENA_2026":
        raise HTTPException(status_code=401, detail="Token no autorizado")

    # 2. Registrar la llegada del archivo en la base de datos
    nuevo_registro = RegistroArchivo(
        nombre_archivo=payload.nombre_archivo,
        estado="input",
        texto_extraido=payload.texto_extraido
    )
    db.add(nuevo_registro)
    
    # 3. Consultar la "Memoria Adaptable" (El Foso)
    # Traemos todas las reglas del cliente específico
    reglas_cliente = db.query(ReglaClasificacion).filter(
        ReglaClasificacion.cliente_id == payload.cliente_id
    ).all()

    cuenta_asignada = None
    retencion_aplicada = False

    # Buscamos si alguna palabra clave registrada por el cliente está en el texto extraído
    texto_lower = payload.texto_extraido.lower()
    for regla in reglas_cliente:
        if regla.palabra_clave.lower() in texto_lower:
            cuenta_asignada = regla.cuenta_contable
            retencion_aplicada = regla.aplica_retencion
            nuevo_registro.estado = "check" # Se clasifica automáticamente, pasa la revisión
            break

    db.commit()

    # 4. Retornar respuesta a n8n para que continúe o detenga el flujo
    return {
        "status": "recibido",
        "accion": "clasificacion_automatica" if cuenta_asignada else "requiere_revision_humana",
        "cuenta_sugerida": cuenta_asignada,
        "aplicar_retencion": retencion_aplicada,
        "id_registro_bd": nuevo_registro.id
    }