from sqlalchemy.orm import Session
from ..models import ReglaClasificacion

def aplicar_memoria_adaptable(db: Session, texto_extraido: str, cliente_id: int = None):
    """
    Busca en el foso de reglas si el texto contiene la palabra_clave aprendida.
    Retorna la cuenta contable y reglas de retención asociadas.
    """
    if not texto_extraido:
        return {"encontrado": False}
        
    texto_lower = texto_extraido.lower()
    
    # Traemos las reglas (puedes filtrar por cliente_id si lo deseas)
    reglas = db.query(ReglaClasificacion).all()
    
    for regla in reglas:
        if regla.palabra_clave and regla.palabra_clave.lower() in texto_lower:
            return {
                "encontrado": True,
                "palabra_clave": regla.palabra_clave,
                "cuenta_contable": regla.cuenta_contable,
                "aplica_retencion": regla.aplica_retencion,
                "porcentaje_retencion": regla.porcentaje_retencion,
                "regla_id": regla.id
            }
            
    return {"encontrado": False}


def registrar_nueva_regla(
    db: Session, 
    palabra_clave: str, 
    cuenta_contable: str, 
    aplica_retencion: bool = False, 
    porcentaje_retencion: float = 0.0, 
    cliente_id: int = None
):
    """
    Enseña al foso una nueva regla contable automatizada.
    """
    existente = db.query(ReglaClasificacion).filter(
        ReglaClasificacion.palabra_clave == palabra_clave.lower()
    ).first()
    
    if existente:
        existente.cuenta_contable = cuenta_contable
        existente.aplica_retencion = aplica_retencion
        existente.porcentaje_retencion = porcentaje_retencion
        db.commit()
        return {"status": "actualizado", "id": existente.id}
    
    nueva_regla = ReglaClasificacion(
        cliente_id=cliente_id,
        palabra_clave=palabra_clave.lower(),
        cuenta_contable=cuenta_contable,
        aplica_retencion=aplica_retencion,
        porcentaje_retencion=porcentaje_retencion
    )
    db.add(nueva_regla)
    db.commit()
    db.refresh(nueva_regla)
    
    return {"status": "aprendido", "id": nueva_regla.id}