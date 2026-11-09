import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Importaciones relativas según la estructura del proyecto
from ..database import get_db
from ..models import RegistroArchivo
from ..services.foso_memoria import aplicar_memoria_adaptable

router = APIRouter(prefix="/api/webhooks", tags=["Ingesta n8n"])

# Mejor práctica: el token vive en una variable de entorno (COLMENA_API_TOKEN).
# Si no existe, se usa el valor actual para no romper tu flujo de n8n.
API_TOKEN = os.getenv("COLMENA_API_TOKEN", "TU_TOKEN_SECRETO_COLMENA_2026")


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
    x_api_token: str = Header(None),
):
    # Seguridad básica para evitar inyecciones de terceros
    if not secrets.compare_digest((x_api_token or "").encode(), API_TOKEN.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")

    # 2. Consultar la "Memoria Adaptable" (El Foso): reglas del cliente + globales
    resultado = aplicar_memoria_adaptable(
        db, payload.texto_extraido, cliente_id=payload.cliente_id
    )

    # 3. Registrar la llegada del archivo (si hay regla, se clasifica y pasa a "check")
    nuevo_registro = RegistroArchivo(
        nombre_archivo=payload.nombre_archivo,
        estado="check" if resultado["encontrado"] else "input",
        texto_extraido=payload.texto_extraido,
    )
    db.add(nuevo_registro)
    try:
        db.commit()
    except IntegrityError:
        # nombre_archivo es único: n8n reintentó o mandó el mismo archivo dos veces
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El archivo '{payload.nombre_archivo}' ya fue recibido.",
        )

    # 4. Retornar respuesta a n8n para que continúe o detenga el flujo
    return {
        "status": "recibido",
        "accion": "clasificacion_automatica" if resultado["encontrado"] else "requiere_revision_humana",
        "cuenta_sugerida": resultado.get("cuenta_contable"),
        "aplicar_retencion": resultado.get("aplica_retencion", False),
        "porcentaje_retencion": resultado.get("porcentaje_retencion", 0.0),
        "regla_id": resultado.get("regla_id"),
        "id_registro_bd": nuevo_registro.id,
    }