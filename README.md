# Blockchain-ZNE

## Aprobaciones multifirma en Stellar (2 de 3)

Puerto de la API: **8001** (`docker compose up --build`). Copia `.env.example` a `.env` y completa:

| Variable | Descripción |
|---|---|
| `COLMENA_API_TOKEN` | Token para el header `X-Api-Token` |
| `N8N_BASE_URL`, `N8N_API_TOKEN`, `N8N_TIMEOUT` | Conexión a n8n (`/webhook/{workflow}`) |
| `STELLAR_NETWORK` | `testnet` (por defecto) o `public` |
| `STELLAR_HORIZON_URL` | URL de Horizon |
| `STELLAR_CUENTA_MULTISIG` | Cuenta pública (G...) con los 3 socios como firmantes |
| `STELLAR_SOCIOS` | Exactamente 3 llaves públicas separadas por coma |
| `STELLAR_UMBRAL` | Firmas requeridas (por defecto 2) |
| `APROBACION_TTL_HORAS` | Vigencia de la aprobación (por defecto 72) |

Las llaves secretas nunca se guardan en el servidor ni en disco.

Configuración inicial (una sola vez, fuera del servidor):
`STELLAR_SETUP_SECRET=S... STELLAR_SOCIOS=G1,G2,G3 python scripts/stellar_setup.py`

Flujo:
1. `POST /api/aprobaciones` con `{"registro_id": 1, "monto": 1000}` crea la aprobación y devuelve `xdr_base`.
2. Cada socio firma localmente: `SOCIO_SECRET=S... python scripts/stellar_firmar.py "<xdr_base>"`.
3. Se sube cada XDR firmado con `POST /api/aprobaciones/{id}/firmas` (`{"xdr_firmado": "..."}`).
4. Con 2 firmas válidas el estado pasa a `aprobada`; `POST /api/aprobaciones/{id}/enviar` la envía a Horizon.

Solo puede haber una aprobación abierta a la vez (comparten el número de secuencia de la cuenta).
