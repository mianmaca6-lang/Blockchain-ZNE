"""
Configuración central por variables de entorno.

Ningún secreto tiene valor por defecto: si falta, la funcionalidad que lo
necesita se niega a operar (fail-closed) en vez de usar un valor inventado.
Los secretos se leen como SecretStr para que no aparezcan en repr() ni en logs.
"""
from functools import lru_cache
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Base de datos ---
    database_url: str = "sqlite:///./data/colmena.db"

    # --- Autenticación de n8n / integraciones (header X-Api-Token) ---
    colmena_api_token: Optional[SecretStr] = None

    # --- Privacidad (Fase 1) ---
    # Clave AES-256-GCM en base64 (32 bytes). Perderla = perder acceso a los registros personales.
    colmena_clave_cifrado: Optional[SecretStr] = None
    colmena_clave_cifrado_version: int = 1
    # Secreto para derivar seudónimos (HMAC). Distinto de la clave de cifrado.
    colmena_secreto_seudonimo: Optional[SecretStr] = None

    # --- Soroban (Fase 1) ---
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    soroban_red: str = "testnet"  # testnet | public
    soroban_contrato_libro_personal: Optional[str] = None  # C...
    # Ruta a un archivo que contiene la llave secreta de la cuenta de servicio.
    # Se prefiere archivo (Docker secret) a variable de entorno.
    soroban_llave_servicio_archivo: Optional[str] = None
    soroban_timeout_s: int = 60

    # --- Respaldos ---
    colmena_backup_dir: str = "./backups"

    # --- Logs ---
    colmena_log_nivel: str = "INFO"


@lru_cache
def obtener_config() -> Configuracion:
    return Configuracion()


def reiniciar_config() -> None:
    """Solo para pruebas: fuerza a releer el entorno."""
    obtener_config.cache_clear()
