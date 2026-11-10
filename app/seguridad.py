import os
import secrets
from typing import Optional

from fastapi import HTTPException, status

# Mismo valor por defecto que app/routers/webhooks.py
_TOKEN_POR_DEFECTO = "TU_TOKEN_SECRETO_COLMENA_2026"


def verificar_token(x_api_token: Optional[str]) -> None:
    """Valida el header X-Api-Token contra COLMENA_API_TOKEN (401 si no coincide)."""
    esperado = os.getenv("COLMENA_API_TOKEN", _TOKEN_POR_DEFECTO)
    if not secrets.compare_digest((x_api_token or "").encode(), esperado.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
