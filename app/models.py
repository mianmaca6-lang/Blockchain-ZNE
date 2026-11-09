from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

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




class Tester(Base):
    __tablename__ = "testers"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True) # Ej. "tester01"
    activo = Column(Boolean, default=True)
    
    logs = relationship("LogTelemetria", back_populates="tester")

class LogTelemetria(Base):
    __tablename__ = "logs_telemetria"
    
    id = Column(Integer, primary_key=True, index=True)
    tester_id = Column(Integer, ForeignKey("testers.id"))
    accion = Column(String)  # Ej. "login", "abrir_registro", "evolucionar"
    detalle = Column(String, nullable=True)
    fecha_hora = Column(String, default=lambda: datetime.now().isoformat())
    
    tester = relationship("Tester", back_populates="logs")

class Transaccion(Base):
    """
    Motor de doble contabilidad para Zine MVP.
    Registra el movimiento exacto del dinero entre cuentas.
    """
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, index=True)
    concepto = Column(String, index=True)       # Ej. "Chocorramo" o "Quincena"
    monto = Column(Float)                       # Ej. 3000 o 1500000
    tipo = Column(String)                       # "ingreso" o "gasto"
    cuenta_origen = Column(String)              # De dónde sale el dinero (Ej. "Bolsillo", "Banco")
    cuenta_destino = Column(String)             # A dónde va (Ej. "Gasto Comida", "Ahorros")
    fecha_hora = Column(String, default=lambda: datetime.now().isoformat())