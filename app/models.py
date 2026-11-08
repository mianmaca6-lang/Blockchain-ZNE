from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String, unique=True, index=True)
    nit = Column(String, unique=True)
    
    # Relación con sus reglas personalizadas (El Foso)
    reglas = relationship("ReglaClasificacion", back_populates="cliente")

class ReglaClasificacion(Base):
    """
    Esta es la memoria adaptable. Si el sistema detecta 'palabra_clave' 
    en una transcripción o factura, aplica esta regla automáticamente.
    """
    __tablename__ = "reglas_clasificacion"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    palabra_clave = Column(String, index=True) # ej: "Autogrúas JCC" o "Gasolina"
    cuenta_contable = Column(String)           # ej: "519595"
    aplica_retencion = Column(Boolean, default=False)
    porcentaje_retencion = Column(Float, default=0.0)
    
    cliente = relationship("Cliente", back_populates="reglas")

class RegistroArchivo(Base):
    """
    Para llevar trazabilidad de lo que hay en 'Base Datos/input' y 'check'
    """
    __tablename__ = "registros_archivos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String, unique=True) # ej: "WhatsApp Audio 2026-11-07..."
    estado = Column(String, default="input")     # "input", "procesado", "check", "error"
    texto_extraido = Column(String, nullable=True)