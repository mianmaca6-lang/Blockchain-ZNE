"""
Configuración única de la cuenta multifirma (ejecutar fuera del servidor).

Variables de entorno (solo en memoria, nunca se escriben a disco):
  STELLAR_SETUP_SECRET  secreto de la cuenta que se convertirá en multisig
  STELLAR_SOCIOS        3 llaves públicas separadas por coma
  STELLAR_NETWORK       testnet (por defecto) | public
  STELLAR_HORIZON_URL   opcional
Tras ejecutar: master_weight=0, umbrales=2, 3 socios con peso 1 (2 de 3).
"""
import os
import sys

import httpx
from stellar_sdk import Keypair, Server, Signer, TransactionBuilder

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.REVISAR_stellar_aprobaciones import ConfigError, parsear_socios, passphrase_de  # noqa: E402


def main() -> int:
    secreto = os.getenv("STELLAR_SETUP_SECRET")
    if not secreto:
        print("Falta STELLAR_SETUP_SECRET", file=sys.stderr)
        return 1
    red = os.getenv("STELLAR_NETWORK", "testnet").strip().lower()
    try:
        socios = parsear_socios(os.getenv("STELLAR_SOCIOS", ""))
        passphrase = passphrase_de(red)
        kp = Keypair.from_secret(secreto)
    except (ConfigError, ValueError) as exc:
        print(f"Configuración inválida: {exc}", file=sys.stderr)
        return 1
    cuenta = kp.public_key
    if kp.public_key in socios:
        print("La cuenta multisig no debe ser uno de los socios", file=sys.stderr)
        return 1
    horizon = os.getenv(
        "STELLAR_HORIZON_URL",
        "https://horizon-testnet.stellar.org" if red == "testnet" else "https://horizon.stellar.org",
    )
    server = Server(horizon)

    if red == "testnet":
        r = httpx.get("https://friendbot.stellar.org", params={"addr": cuenta}, timeout=30)
        if r.status_code not in (200, 400):  # 400: ya estaba fondeada
            print(f"Friendbot falló: {r.status_code}", file=sys.stderr)
            return 1

    builder = TransactionBuilder(
        source_account=server.load_account(cuenta),
        network_passphrase=passphrase,
        base_fee=100,
    )
    for socio in socios:
        builder.append_set_options_op(signer=Signer.ed25519_public_key(socio, 1))
    builder.append_set_options_op(master_weight=0, low_threshold=2, med_threshold=2, high_threshold=2)
    tx = builder.set_timeout(120).build()
    tx.sign(kp)
    resp = server.submit_transaction(tx)

    print(f"Cuenta multisig configurada: {cuenta}")
    print(f"Hash: {resp.get('hash')}")
    print(f"Defina STELLAR_CUENTA_MULTISIG={cuenta} en su .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
