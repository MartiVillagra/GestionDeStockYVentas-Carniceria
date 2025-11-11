#aqui vamos a crear las tablas de la base de datos

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Producto(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre_producto = Column(String, nullable=False)
    categoria = Column(String)
    precio_kilo = Column(Float, nullable=False)
    tipo_venta = Column(String, nullable=False)
    stock_kilos = Column(Float, default=0)
    stock_unidades = Column(Float, default=0)
    peso_unidad_kg = Column(Float, default=0.0)

class CajaSesion(Base):
    __tablename__ = "caja_sesion"
    id_sesion = Column(Integer, primary_key=True, index=True)
    id_empleado = Column(Integer, default=1)
    fecha_apertura = Column(DateTime(timezone=True), server_default=func.now())
    monto_inicial = Column(Float, nullable=False)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    monto_contado = Column(Float, nullable=True)
    comentarios = Column(Text, nullable=True)

class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"
    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_sesion = Column(Integer, ForeignKey("caja_sesion.id_sesion"))
    tipo_movimiento = Column(String)
    monto = Column(Float)
    descripcion = Column(String)
    fecha_movimiento = Column(DateTime(timezone=True), server_default=func.now())